# EREV 요청형 26 kW Electrical FMU

2026-11-08. 기존 입력 감사와 요청 인터페이스 준비 커밋 e5194cf 다음 구현 배치다.

EREV_Request26.fmu는 FMI 2.0 Co-Simulation의 win64 DLL과 linux64 SO를 포함한다. 전압, ON 요청, 실제 DC 부하, 배터리 충전수용 전력, 보호 OFF 입력을 받으며 발전전력·목표·상태·기동횟수·타이머·부호 있는 단자전력·에너지를 출력한다. VR/단위 표는 BUILD_MANIFEST.json과 modelDescription.xml에 있다.

기존 가정인 상한 26 kW, 지연 0.5 s, 상승 20 kW/s, 하강 50 kW/s, 최소 ON 10 s/OFF 5 s를 유지한다. 최소 ON은 STARTING 진입부터, OFF는 영출력 OFF 진입부터 센다. 충전수용 제한과 보호가 램프/유지시간보다 우선한다. 초기 OFF 대기는 충족된 상태다.

전류 기본 부호는 기존 T1과 동일하다. 공급할 때 I_terminal_A와 P_terminal_W는 음수, P_generated_W와 E_generated_J는 양수다. request_on과 protection_off는 Real 값 0.5 이상을 true로 해석한다. 충전허용전력은 양수 W다. 기본 요청/부하/충전허용은 0이다.

전압 100–500 V 범위는 기존 T1 FMU의 수치 운전창을 계승했다. 실제 장치의 허용전압으로 검증된 값은 아니다. 범위 밖 전압과 protection_off는 즉시 단자 공급을 0으로 만든다. 회생부하 자체가 충전수용을 넘는 문제는 차량 회생제어에서 처리한다.

doStep에서 입력을 통신 구간 동안 유지하고 구간 끝에 상태를 갱신한다. 요청/상태 전이는 최대 한 통신 간격 양자화가 있으므로 2 ms를 사용한다. fmi2GetReal은 상태를 변경하지 않는다. 서로 다른 FMU 인스턴스는 상태를 공유하지 않는다. 입력 갱신 실패와 잘못된 시간 스텝은 상태 변경 전에 거절한다. FMI state serialization/rollback은 지원하지 않는 것으로 선언된 기본값을 따른다.

실제 linux64 바이너리를 ctypes로 호출해 기존 Python 참조와 비교했다. 짧은 요청·재기동 대기·충전수용 감소·비상보호·0 V·회생의 여섯 시나리오에서 각 10,000 스텝의 전력·전류·상태·기동횟수가 일치했다. 인스턴스 분리·reset·입력 실패의 원자성도 확인했다. 테스트 결과와 표본 로그는 TEST_RESULTS.json 및 test_traces에 있다.

Windows DLL은 Zig 0.13.0의 x86_64-windows-msvc 대상으로 컴파일했다. DLL의 64비트 PE 형식, FMI export, import/TLS 부재를 검사했다. 공식 FMI 2.0.5 XSD 검증을 통과했다. 이 환경에서 Windows DLL의 CRUISE M 실행은 확인하지 못했다.

현재 배치의 완료조건은 요청형 FMU 구현·바이너리 생성·참조 및 구조 검증이다. 다음 배치는 CRUISE M 사본에 시험 요청 입력과 실제 집계를 연결하는 작업이다. 기존 발전계는 OFF로 유지하고 새 공급원만 실제 버스에 주입해야 한다.
{
  "stage": "REQUEST_FMU_IMPLEMENTED_AND_OFFLINE_VERIFIED",
  "status": "COMPLETE",
  "original_protocol_preserved": true,
  "CRUISE_runs": 0,
  "tests": {
    "status": "BINARY_REFERENCE_TESTS_PASS",
    "checks": {
      "short_request": {
        "binary_reference_agreement": "PASS",
        "samples": 10000,
        "starts": 1
      },
      "restart_dwell": {
        "binary_reference_agreement": "PASS",
        "samples": 10000,
        "starts": 2
      },
      "charge_curtail": {
        "binary_reference_agreement": "PASS",
        "samples": 10000,
        "starts": 1
      },
      "emergency": {
        "binary_reference_agreement": "PASS",
        "samples": 10000,
        "starts": 2
      },
      "zero_voltage": {
        "binary_reference_agreement": "PASS",
        "samples": 10000,
        "starts": 2
      },
      "regeneration": {
        "binary_reference_agreement": "PASS",
        "samples": 10000,
        "starts": 1
      },
      "instance_isolation_reset_and_atomic_errors": "PASS"
    },
    "CRUISE_M_runs": 0,
    "sampling": "End-of-communication-interval update with held inputs. Request edge latency up to one communication step.",
    "windows_execution": "Not executed on Windows in this environment"
  },
  "fmu_sha256": "6cca9fd6f20595387df9924d27dfccc9540efa712409664667477002571d6294",
  "next_start": "Build request-test project and replace generator aggregation signals"
}
#include <stddef.h>
#ifdef _WIN32
#define API __declspec(dllexport)
#else
#define API
#endif

typedef unsigned int VR;
typedef void *Component;
typedef const char *String;
typedef int Status;
typedef struct {
    void (*logger)(void *, String, Status, String, String, ...);
    void *(*allocateMemory)(size_t, size_t);
    void (*freeMemory)(void *);
    void (*stepFinished)(void *, Status);
    void *environment;
} Callbacks;

enum { OK, WARNING, DISCARD, ERROR };
enum { OFF, STARTING, RAMP, RUN, STOPPING };
enum {
    VOLTAGE, CURRENT, GENERATED, SIGN, REQUEST, LOAD, CHARGE, PROTECTION,
    TARGET, STATE, STARTS, ON_ELAPSED, OFF_ELAPSED, PROTECTED, TERMINAL_POWER,
    GENERATED_ENERGY
};
typedef struct {
    void (*release)(void *);
    double time, voltage, sign, request, load, charge, protection;
    double power, on_since, off_since, energy;
    int state, starts, initialized, terminated;
} Bench;

static double smaller(double a, double b) { return a < b ? a : b; }
static double larger(double a, double b) { return a > b ? a : b; }
static double absolute(double a) { return a < 0 ? -a : a; }
static int finite_number(double a) { return a == a && a <= 1.7976931348623157e308 && a >= -1.7976931348623157e308; }
static int protected_now(const Bench *b) {
    /* Inherited numerical operating window of the accepted T1 source. */
    return b->protection >= 0.5 || b->voltage < 100.0 || b->voltage > 500.0;
}
static double target(const Bench *b) {
    return smaller(26000.0, larger(0.0, b->load + b->charge));
}
static double delivered(const Bench *b) {
    return protected_now(b) ? 0.0 : smaller(b->power, target(b));
}
static void defaults(Bench *b) {
    b->time = 0.0;
    b->voltage = 0.0;
    b->sign = -1.0;
    b->request = b->load = b->charge = b->protection = 0.0;
    b->power = b->on_since = b->energy = 0.0;
    b->off_since = -5.0;
    b->state = OFF;
    b->starts = b->initialized = b->terminated = 0;
}
static void sample(Bench *b, double t, double dt) {
    double command = target(b);
    if (protected_now(b)) {
        if (b->state != OFF || b->power > 0.0) b->off_since = t;
        b->state = OFF;
        b->power = 0.0;
        b->on_since = 0.0;
        return;
    }
    if (b->state == OFF && b->request >= 0.5 && t - b->off_since >= 5.0 - 1e-9) {
        b->state = STARTING;
        b->on_since = t;
        b->starts += 1;
    }
    if (b->state == STARTING && t - b->on_since >= 0.5 - 1e-9) {
        b->state = RAMP;
        dt = 0.0;
    }
    if ((b->state == STARTING || b->state == RAMP || b->state == RUN) &&
        b->request < 0.5 && t - b->on_since >= 10.0 - 1e-9) {
        b->state = STOPPING;
        dt = 0.0;
    }
    if (b->state == STARTING) {
        b->power = 0.0;
    } else if (b->state == RAMP || b->state == RUN) {
        if (command >= b->power) b->power += smaller(command - b->power, 20000.0 * dt);
        else b->power += larger(command - b->power, -50000.0 * dt);
        b->state = absolute(b->power - command) < 1e-6 ? RUN : RAMP;
    } else if (b->state == STOPPING) {
        b->power = larger(0.0, b->power - 50000.0 * dt);
        if (b->power <= 1e-6) {
            b->power = 0.0;
            b->state = OFF;
            b->off_since = t;
            b->on_since = 0.0;
        }
    }
    /* Charge acceptance has priority over a normal ramp-down constraint. */
    b->power = smaller(b->power, command);
}

API String fmi2GetTypesPlatform(void) { return "default"; }
API String fmi2GetVersion(void) { return "2.0"; }
API Status fmi2SetDebugLogging(Component c, int on, size_t n, const String categories[]) { return c ? OK : ERROR; }
API Component fmi2Instantiate(String name, int kind, String guid, String resources,
                         const Callbacks *cb, int visible, int logging) {
    Bench *b;
    if (kind != 1 || !cb || !cb->allocateMemory || !cb->freeMemory) return 0;
    b = cb->allocateMemory(1, sizeof(Bench));
    if (!b) return 0;
    b->release = cb->freeMemory;
    defaults(b);
    return b;
}
API void fmi2FreeInstance(Component c) {
    Bench *b = c;
    if (b) b->release(b);
}
API Status fmi2SetupExperiment(Component c, int td, double tolerance, double start,
                           int sd, double stop) {
    Bench *b = c;
    if (!b || b->initialized || !finite_number(start) || start < 0.0) return ERROR;
    if (sd && (!finite_number(stop) || stop < start)) return ERROR;
    b->time = start;
    b->off_since = start - 5.0;
    return OK;
}
API Status fmi2EnterInitializationMode(Component c) { return c ? OK : ERROR; }
API Status fmi2ExitInitializationMode(Component c) {
    Bench *b = c;
    if (!b || b->terminated) return ERROR;
    b->initialized = 1;
    return OK;
}
API Status fmi2Terminate(Component c) {
    Bench *b = c;
    if (!b) return ERROR;
    b->terminated = 1;
    return OK;
}
API Status fmi2Reset(Component c) {
    if (!c) return ERROR;
    defaults(c);
    return OK;
}
API Status fmi2GetReal(Component c, const VR refs[], size_t n, double values[]) {
    Bench *b = c;
    double power;
    if (!b || (n && (!refs || !values))) return ERROR;
    for (size_t j = 0; j < n; ++j) if (refs[j] > GENERATED_ENERGY) return ERROR;
    power = delivered(b);
    for (size_t j = 0; j < n; ++j) {
        switch (refs[j]) {
        case VOLTAGE: values[j] = b->voltage; break;
        case CURRENT: values[j] = protected_now(b) ? 0.0 : b->sign * power / b->voltage; break;
        case GENERATED: values[j] = power; break;
        case SIGN: values[j] = b->sign; break;
        case REQUEST: values[j] = b->request; break;
        case LOAD: values[j] = b->load; break;
        case CHARGE: values[j] = b->charge; break;
        case PROTECTION: values[j] = b->protection; break;
        case TARGET: values[j] = target(b); break;
        case STATE: values[j] = b->state; break;
        case STARTS: values[j] = b->starts; break;
        case ON_ELAPSED: values[j] = b->state == OFF ? 0.0 : b->time - b->on_since; break;
        case OFF_ELAPSED: values[j] = b->state == OFF ? larger(0.0, b->time - b->off_since) : 0.0; break;
        case PROTECTED: values[j] = protected_now(b); break;
        case TERMINAL_POWER: values[j] = b->sign * power; break;
        case GENERATED_ENERGY: values[j] = b->energy; break;
        }
    }
    return OK;
}
API Status fmi2SetReal(Component c, const VR refs[], size_t n, const double values[]) {
    Bench *b = c;
    if (!b || (n && (!refs || !values))) return ERROR;
    /* Validate the whole update before applying any value. */
    for (size_t j = 0; j < n; ++j) {
        VR r = refs[j];
        if (!finite_number(values[j])) return ERROR;
        if (!(r == VOLTAGE || r == SIGN || r == REQUEST || r == LOAD || r == CHARGE || r == PROTECTION)) return ERROR;
        if (r == SIGN && (b->initialized || (values[j] != -1.0 && values[j] != 1.0))) return ERROR;
        if (r == CHARGE && values[j] < 0.0) return ERROR;
    }
    for (size_t j = 0; j < n; ++j) {
        switch (refs[j]) {
        case VOLTAGE: b->voltage = values[j]; break;
        case SIGN: b->sign = values[j]; break;
        case REQUEST: b->request = values[j]; break;
        case LOAD: b->load = values[j]; break;
        case CHARGE: b->charge = values[j]; break;
        case PROTECTION: b->protection = values[j]; break;
        }
    }
    return OK;
}
API Status fmi2DoStep(Component c, double t, double dt, int noRollback) {
    Bench *b = c;
    double before;
    if (!b || !b->initialized || b->terminated) return ERROR;
    if (!finite_number(t) || !finite_number(dt) || dt <= 0.0 || t < 0.0) return ERROR;
    if (!finite_number(t + dt) || t + dt <= t || absolute(t - b->time) > 1e-8) return ERROR;
    before = delivered(b);
    /* Inputs are held over the communication interval, sampled at its end. */
    sample(b, t + dt, dt);
    b->time = t + dt;
    b->energy += 0.5 * (before + delivered(b)) * dt;
    return OK;
}
API Status fmi2CancelStep(Component c) { return ERROR; }
#define UNUSED_TYPE(Name, Type) \
 API Status fmi2Get##Name(Component c, const VR r[], size_t n, Type v[]) { return c && !n ? OK : ERROR; } \
 API Status fmi2Set##Name(Component c, const VR r[], size_t n, const Type v[]) { return c && !n ? OK : ERROR; }
UNUSED_TYPE(Integer, int)
UNUSED_TYPE(Boolean, int)
UNUSED_TYPE(String, String)
API Status fmi2GetFMUstate(Component c, void **state) { return ERROR; }
API Status fmi2SetFMUstate(Component c, void *state) { return ERROR; }
API Status fmi2FreeFMUstate(Component c, void **state) { return ERROR; }
API Status fmi2SerializedFMUstateSize(Component c, void *state, size_t *size) { return ERROR; }
API Status fmi2SerializeFMUstate(Component c, void *state, char data[], size_t size) { return ERROR; }
API Status fmi2DeSerializeFMUstate(Component c, const char data[], size_t size, void **state) { return ERROR; }
API Status fmi2GetDirectionalDerivative(Component c, const VR a[], size_t na, const VR b[], size_t nb,
                                    const double dv[], double dz[]) { return ERROR; }
API Status fmi2SetRealInputDerivatives(Component c, const VR r[], size_t n, const int order[], const double v[]) { return ERROR; }
API Status fmi2GetRealOutputDerivatives(Component c, const VR r[], size_t n, const int order[], double v[]) { return ERROR; }
API Status fmi2GetStatus(Component c, int k, Status *v) { if (!c || k != 0) return DISCARD; *v = OK; return OK; }
API Status fmi2GetRealStatus(Component c, int k, double *v) { if (!c || k != 2) return DISCARD; *v = ((Bench *)c)->time; return OK; }
API Status fmi2GetIntegerStatus(Component c, int k, int *v) { return DISCARD; }
API Status fmi2GetBooleanStatus(Component c, int k, int *v) { if (!c || k != 3) return DISCARD; *v = 0; return OK; }
API Status fmi2GetStringStatus(Component c, int k, String *v) { return DISCARD; }

#ifdef _WIN32
int DllMain(void *module, unsigned long reason, void *reserved) { return 1; }
#endif
