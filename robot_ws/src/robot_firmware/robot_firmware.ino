

const float TICKS_PER_REVOLUTION = 1440.0f; 
const float WHEEL_RADIUS_M = 0.0325f; 
const float TRACK_WIDTH_M = 0.20f; 

const unsigned long CONTROL_DT_MS = 20; 
const unsigned long CMD_TIMEOUT_MS = 500; 

const uint8_t PIN_LEFT_EN = 22;
const uint8_t PIN_LEFT_RPWM = 5;
const uint8_t PIN_LEFT_LPWM = 6;

const uint8_t PIN_RIGHT_EN = 23;
const uint8_t PIN_RIGHT_RPWM = 9;
const uint8_t PIN_RIGHT_LPWM = 10;

const uint8_t PIN_LEFT_A = 2;
const uint8_t PIN_LEFT_B = 3;
const uint8_t PIN_RIGHT_A = 18;
const uint8_t PIN_RIGHT_B = 19;

static const int8_t QUAD_TRANSITIONS[16] = {
  0, +1, -1, 0,
  -1, 0, 0, +1,
  +1, 0, 0, -1,
   0, -1, +1, 0
};

volatile long g_left_ticks = 0;
volatile long g_right_ticks = 0;
volatile uint8_t g_left_state = 0;
volatile uint8_t g_right_state = 0;

int g_cmd_left = 0;
int g_cmd_right = 0;
unsigned long g_last_cmd_ms = 0;

const size_t SERIAL_BUF_LEN = 48;
char g_serial_buf[SERIAL_BUF_LEN];
size_t g_serial_len = 0;

unsigned long g_last_loop_ms = 0;
long g_prev_left_ticks = 0;
long g_prev_right_ticks = 0;

float g_v_mps = 0.0f;
float g_omega_rps = 0.0f;

static inline uint8_t readQuadState(uint8_t pin_a, uint8_t pin_b) {
  return (uint8_t)((digitalRead(pin_a) << 1) | digitalRead(pin_b));
}

void leftEncoderISR() {
  uint8_t curr = readQuadState(PIN_LEFT_A, PIN_LEFT_B);
  uint8_t idx = (uint8_t)((g_left_state << 2) | curr);
  g_left_ticks += QUAD_TRANSITIONS[idx];
  g_left_state = curr;
}

void rightEncoderISR() {
  uint8_t curr = readQuadState(PIN_RIGHT_A, PIN_RIGHT_B);
  uint8_t idx = (uint8_t)((g_right_state << 2) | curr);
  g_right_ticks += QUAD_TRANSITIONS[idx];
  g_right_state = curr;
}

static int clampPwm(int value) {
  if (value > 255) {
    return 255;
