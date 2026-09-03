

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
  }
  if (value < -255) {
    return -255;
  }
  return value;
}

void setSidePwm(uint8_t pin_en, uint8_t pin_rpwm, uint8_t pin_lpwm, int pwm) {
  pwm = clampPwm(pwm);
  if (pwm == 0) {
    digitalWrite(pin_en, LOW);
    analogWrite(pin_rpwm, 0);
    analogWrite(pin_lpwm, 0);
    return;
  }

  digitalWrite(pin_en, HIGH);
  if (pwm > 0) {
    analogWrite(pin_rpwm, pwm);
    analogWrite(pin_lpwm, 0);
  } else {
    analogWrite(pin_rpwm, 0);
    analogWrite(pin_lpwm, -pwm);
  }
}

void applyMotorCommand(int left_pwm, int right_pwm) {
  setSidePwm(PIN_LEFT_EN, PIN_LEFT_RPWM, PIN_LEFT_LPWM, left_pwm);
  setSidePwm(PIN_RIGHT_EN, PIN_RIGHT_RPWM, PIN_RIGHT_LPWM, right_pwm);
}

void stopMotors() {
  g_cmd_left = 0;
  g_cmd_right = 0;
  applyMotorCommand(0, 0);
}

bool parseMotorCommand(const char *line) {
  int left_pwm = 0;
  int right_pwm = 0;

  
  if (sscanf(line, "L%d R%d", &left_pwm, &right_pwm) != 2) {
    if (sscanf(line, "L %d R %d", &left_pwm, &right_pwm) != 2) {
      return false;
    }
  }

  g_cmd_left = clampPwm(left_pwm);
  g_cmd_right = clampPwm(right_pwm);
  g_last_cmd_ms = millis();
  applyMotorCommand(g_cmd_left, g_cmd_right);
  return true;
}

void pollSerial() {
  while (Serial.available() > 0) {
    char c = (char)Serial.read();
    if (c == '\r') {
      continue;
    }
    if (c == '\n') {
      g_serial_buf[g_serial_len] = '\0';
      if (g_serial_len > 0) {
        parseMotorCommand(g_serial_buf);
      }
      g_serial_len = 0;
      continue;
    }
    if (g_serial_len + 1 < SERIAL_BUF_LEN) {
