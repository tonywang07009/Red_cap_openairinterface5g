#include "aiotf_inventory.h"

#include <arpa/inet.h>
#include <assert.h>
#include <ctype.h>
#include <errno.h>
#include <fcntl.h>
#include <poll.h>
#include <signal.h>
#include <stdarg.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>
#include <sys/socket.h>
#include <sys/time.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>

#define AIOTF_DEFAULT_ADDRESS "0.0.0.0"
#define AIOTF_DEFAULT_PORT 36900U
#define AIOTF_DEFAULT_TIMEOUT_MS 5000U
#define AIOTF_DEFAULT_NRF_URI "http://oai-nrf:8080"
#define AIOTF_DEFAULT_NRF_TIMEOUT_MS 1000U
#define AIOTF_DEFAULT_NRF_RETRY_MS 5000U
#define AIOTF_DEFAULT_SBI_ADDRESS "0.0.0.0"
#define AIOTF_DEFAULT_SBI_PORT 8080U
#define AIOTF_DEFAULT_TRUSTED_AF_ID "trusted-af"
#define AIOTF_DEFAULT_NF_INSTANCE_ID "11111111-2222-4333-8444-555555558601"
#define AIOTF_DEFAULT_NF_ADDRESS "192.168.70.141"
#define AIOTF_DEFAULT_MCC "001"
#define AIOTF_DEFAULT_MNC "01"
#define AIOTF_DEFAULT_AIOT_AREA_CODE "000001"
#define AIOTF_STATUS_PATH "/tmp/oai-aiotf.status"
#define AIOTF_NRF_URI_MAX 255U
#define AIOTF_NRF_RESPONSE_MAX 32767U
#define AIOTF_NRF_PROFILE_MAX 1023U
#define AIOTF_UUID_LENGTH 36U
#define AIOTF_DIAGNOSTIC_WIRE_SIZE 40U
#define AIOTF_DIAGNOSTIC_MAGIC 0x41494f54U
#define AIOTF_DIAGNOSTIC_VERSION 1U
#define AIOTF_DIAGNOSTIC_CRC_VALID 0x0001U
#define AIOTF_DIAGNOSTIC_MAX_FRAME 1023U
#define AIOTF_DIAGNOSTIC_MAX_SLOT 159U
#define AIOTF_NAIOTF_PATH "/naiotf-aiot/v1/request-inv"
#define AIOTF_HTTP_REQUEST_MAX 16384U
#define AIOTF_JSON_OUTPUT_MAX 8191U
#define AIOTF_URI_MAX 1023U
#define AIOTF_AF_ID_MAX 127U
#define AIOTF_TRANS_ID_MAX 95U
#define AIOTF_CALLBACK_RETRY_MS 5000U

typedef enum {
  AIOTF_PROFILE_INVALID = 0,
  AIOTF_PROFILE_EXPERIMENTAL_N6,
  AIOTF_PROFILE_TRUSTED_AF_SBI,
  AIOTF_PROFILE_THIRD_PARTY_AF_NEF,
} aiotf_profile_t;

typedef enum {
  AIOTF_CONFIG_OK = 0,
  AIOTF_CONFIG_INVALID_ARGUMENT,
  AIOTF_CONFIG_DUPLICATE_OPTION,
  AIOTF_CONFIG_INVALID_PROFILE,
  AIOTF_CONFIG_PROFILE_UNAVAILABLE,
  AIOTF_CONFIG_INVALID_ADDRESS,
  AIOTF_CONFIG_INVALID_PORT,
  AIOTF_CONFIG_INVALID_TAGS,
  AIOTF_CONFIG_INVALID_TIMEOUT,
  AIOTF_CONFIG_INVALID_PENDING_CONTEXT,
  AIOTF_CONFIG_INVALID_NRF_URI,
  AIOTF_CONFIG_INVALID_NF_INSTANCE_ID,
  AIOTF_CONFIG_INVALID_NF_ADDRESS,
  AIOTF_CONFIG_INVALID_PLMN,
  AIOTF_CONFIG_INVALID_AIOT_AREA_CODE,
  AIOTF_CONFIG_INVALID_NRF_TIMEOUT,
  AIOTF_CONFIG_INVALID_NRF_RETRY,
  AIOTF_CONFIG_INVALID_SBI_ADDRESS,
  AIOTF_CONFIG_INVALID_SBI_PORT,
  AIOTF_CONFIG_INVALID_TRUSTED_AF_ID,
} aiotf_config_status_t;

typedef enum {
  AIOTF_NRF_OK = 0,
  AIOTF_NRF_HTTP_REJECTED,
  AIOTF_NRF_TIMEOUT,
  AIOTF_NRF_UNAVAILABLE,
  AIOTF_NRF_READBACK_REJECTED,
  AIOTF_NRF_DISCOVERY_REJECTED,
  AIOTF_NRF_INTERNAL_ERROR,
} aiotf_nrf_status_t;

typedef struct {
  uint64_t correlation_id;
  uint64_t session_id;
  uint32_t tag_id;
  uint32_t binding_epoch;
  uint32_t frame;
  uint32_t slot;
  aiotf_reader_mode_t reader_mode;
} aiotf_pending_context_config_t;

typedef struct {
  aiotf_profile_t profile;
  char listen_address[INET_ADDRSTRLEN];
  uint16_t listen_port;
  uint32_t tag_ids[AIOTF_MAX_TAGS];
  size_t tag_count;
  uint32_t timeout_ms;
  aiotf_pending_context_config_t pending_contexts[AIOTF_MAX_TAGS];
  size_t pending_context_count;
  char nrf_uri[AIOTF_NRF_URI_MAX + 1];
  char nf_instance_id[AIOTF_UUID_LENGTH + 1];
  char nf_address[INET_ADDRSTRLEN];
  char mcc[4];
  char mnc[4];
  char aiot_area_code[7];
  uint32_t nrf_timeout_ms;
  uint32_t nrf_retry_ms;
  char sbi_address[INET_ADDRSTRLEN];
  uint16_t sbi_port;
  char trusted_af_id[AIOTF_AF_ID_MAX + 1];
} aiotf_config_t;

typedef struct {
  bool event_loop_running;
  bool state_initialized;
  bool diagnostic_listener_bound;
  bool sbi_listener_bound;
  bool nrf_registered;
  bool amf_available;
  bool nef_available;
} aiotf_dependencies_t;

typedef struct {
  bool live;
  bool ready;
  const char *reason;
} aiotf_health_t;

typedef struct {
  int curl_exit;
  long http_code;
  char body[AIOTF_NRF_RESPONSE_MAX + 1];
} aiotf_http_response_t;

typedef struct {
  char af_id[AIOTF_AF_ID_MAX + 1];
  char notif_uri[AIOTF_URI_MAX + 1];
  uint32_t tag_ids[AIOTF_MAX_TAGS];
  size_t tag_count;
  uint32_t timeout_ms;
} aiotf_naiotf_request_t;

typedef struct {
  bool active;
  bool notification_sent;
  char trans_id[AIOTF_TRANS_ID_MAX + 1];
  char notif_uri[AIOTF_URI_MAX + 1];
  aiotf_report_arbitration_t transactions[AIOTF_MAX_TAGS];
  size_t transaction_count;
  uint64_t deadline_ms;
  uint64_t last_notification_attempt_ms;
} aiotf_inventory_operation_t;

static volatile sig_atomic_t stop_requested;

static bool run_curl(const char *method,
                     const char *url,
                     const char *payload,
                     uint32_t timeout_ms,
                     aiotf_http_response_t *response);
static bool write_all(int fd, const char *buffer, size_t size);
static uint64_t monotonic_ms(void);
static bool parse_naiotf_request(const char *body,
                                 size_t body_size,
                                 const aiotf_config_t *config,
                                 aiotf_naiotf_request_t *request,
                                 const char **reason);
static bool start_inventory_operation(aiotf_inventory_context_t *context,
                                      const aiotf_binding_table_t *bindings,
                                      const aiotf_config_t *config,
                                      const aiotf_naiotf_request_t *request,
                                      uint64_t now_ms,
                                      aiotf_inventory_operation_t *operation,
                                      const char **reason);

static const char *profile_name(aiotf_profile_t profile)
{
  switch (profile) {
    case AIOTF_PROFILE_EXPERIMENTAL_N6:
      return "experimental_n6";
    case AIOTF_PROFILE_TRUSTED_AF_SBI:
      return "trusted_af_sbi";
    case AIOTF_PROFILE_THIRD_PARTY_AF_NEF:
      return "third_party_af_nef";
    default:
      return "invalid";
  }
}

static aiotf_profile_t parse_profile(const char *value)
{
  if (value == NULL)
    return AIOTF_PROFILE_INVALID;
  if (strcmp(value, "experimental_n6") == 0)
    return AIOTF_PROFILE_EXPERIMENTAL_N6;
  if (strcmp(value, "trusted_af_sbi") == 0)
    return AIOTF_PROFILE_TRUSTED_AF_SBI;
  if (strcmp(value, "third_party_af_nef") == 0)
    return AIOTF_PROFILE_THIRD_PARTY_AF_NEF;
  return AIOTF_PROFILE_INVALID;
}

static aiotf_config_status_t parse_port(const char *value, uint16_t *port)
{
  if (value == NULL || port == NULL || value[0] == '\0' || value[0] == '-' || value[0] == '+')
    return AIOTF_CONFIG_INVALID_PORT;

  char *end = NULL;
  errno = 0;
  const unsigned long parsed = strtoul(value, &end, 10);
  if (errno != 0 || end == value || *end != '\0' || parsed == 0 || parsed > UINT16_MAX)
    return AIOTF_CONFIG_INVALID_PORT;
  *port = (uint16_t)parsed;
  return AIOTF_CONFIG_OK;
}

static bool parse_u64(const char *value, uint64_t minimum, uint64_t maximum, uint64_t *result)
{
  if (value == NULL || result == NULL || value[0] == '\0' || value[0] == '-' || value[0] == '+')
    return false;
  char *end = NULL;
  errno = 0;
  const unsigned long long parsed = strtoull(value, &end, 10);
  if (errno != 0 || end == value || *end != '\0' || parsed < minimum || parsed > maximum)
    return false;
  *result = (uint64_t)parsed;
  return true;
}

static aiotf_config_status_t parse_tags(const char *value, aiotf_config_t *config)
{
  if (value == NULL || config == NULL || value[0] == '\0')
    return AIOTF_CONFIG_INVALID_TAGS;

  const size_t length = strlen(value);
  if (length >= 256 || value[0] == ',' || value[length - 1] == ',' || strstr(value, ",,") != NULL)
    return AIOTF_CONFIG_INVALID_TAGS;

  char copy[256];
  memcpy(copy, value, length + 1);
  bool selected[AIOTF_MAX_TAGS + 1] = {false};
  size_t count = 0;
  char *save = NULL;
  for (char *token = strtok_r(copy, ",", &save); token != NULL; token = strtok_r(NULL, ",", &save)) {
    char *end = NULL;
    errno = 0;
    const unsigned long tag_id = strtoul(token, &end, 10);
    if (errno != 0 || end == token || *end != '\0' || tag_id == 0 || tag_id > AIOTF_MAX_TAGS
        || selected[tag_id] || count == AIOTF_MAX_TAGS)
      return AIOTF_CONFIG_INVALID_TAGS;
    selected[tag_id] = true;
    config->tag_ids[count++] = (uint32_t)tag_id;
  }
  if (count == 0)
    return AIOTF_CONFIG_INVALID_TAGS;
  config->tag_count = count;
  return AIOTF_CONFIG_OK;
}

static aiotf_config_status_t parse_timeout(const char *value, uint32_t *timeout_ms)
{
  uint64_t parsed = 0;
  if (!parse_u64(value, 1, UINT32_MAX, &parsed) || timeout_ms == NULL)
    return AIOTF_CONFIG_INVALID_TIMEOUT;
  *timeout_ms = (uint32_t)parsed;
  return AIOTF_CONFIG_OK;
}

static bool valid_http_uri(const char *value)
{
  if (value == NULL || strncmp(value, "http://", 7) != 0 || value[7] == '\0' || strlen(value) > AIOTF_NRF_URI_MAX)
    return false;
  for (const char *cursor = value + 7; *cursor != '\0'; ++cursor) {
    if (!isalnum((unsigned char)*cursor) && strchr(".-:/_", *cursor) == NULL)
      return false;
  }
  return true;
}

static bool valid_uuid(const char *value)
{
  if (value == NULL || strlen(value) != AIOTF_UUID_LENGTH)
    return false;
  for (size_t i = 0; i < AIOTF_UUID_LENGTH; ++i) {
    const bool separator = i == 8 || i == 13 || i == 18 || i == 23;
    if ((separator && value[i] != '-') || (!separator && !isxdigit((unsigned char)value[i])))
      return false;
  }
  return true;
}

static bool valid_digits(const char *value, size_t minimum, size_t maximum)
{
  if (value == NULL || strlen(value) < minimum || strlen(value) > maximum)
    return false;
  for (const char *cursor = value; *cursor != '\0'; ++cursor) {
    if (!isdigit((unsigned char)*cursor))
      return false;
  }
  return true;
}

static bool valid_aiot_area_code(const char *value)
{
  if (value == NULL || strlen(value) != 6)
    return false;
  for (const char *cursor = value; *cursor != '\0'; ++cursor) {
    if (!isxdigit((unsigned char)*cursor))
      return false;
  }
  return true;
}

static bool valid_af_id(const char *value)
{
  if (value == NULL || value[0] == '\0' || strlen(value) > AIOTF_AF_ID_MAX)
    return false;
  for (const char *cursor = value; *cursor != '\0'; ++cursor) {
    if (!isalnum((unsigned char)*cursor) && strchr(".-_:", *cursor) == NULL)
      return false;
  }
  return true;
}

static aiotf_config_status_t parse_pending_context(const char *value, aiotf_config_t *config)
{
  if (value == NULL || config == NULL || config->pending_context_count == AIOTF_MAX_TAGS || strlen(value) >= 160)
    return AIOTF_CONFIG_INVALID_PENDING_CONTEXT;

  char copy[160];
  snprintf(copy, sizeof(copy), "%s", value);
  char *fields[7] = {0};
  char *save = NULL;
  size_t field_count = 0;
  for (char *field = strtok_r(copy, ":", &save); field != NULL; field = strtok_r(NULL, ":", &save)) {
    if (field_count == 7)
      return AIOTF_CONFIG_INVALID_PENDING_CONTEXT;
    fields[field_count++] = field;
  }
  if (field_count != 7)
    return AIOTF_CONFIG_INVALID_PENDING_CONTEXT;

  uint64_t tag_id = 0;
  uint64_t correlation_id = 0;
  uint64_t session_id = 0;
  uint64_t binding_epoch = 0;
  uint64_t frame = 0;
  uint64_t slot = 0;
  if (!parse_u64(fields[0], 1, AIOTF_MAX_TAGS, &tag_id)
      || (strcmp(fields[1], "normal") != 0 && strcmp(fields[1], "diversity") != 0)
      || !parse_u64(fields[2], 1, UINT64_MAX, &correlation_id)
      || !parse_u64(fields[3], 1, UINT64_MAX, &session_id)
      || !parse_u64(fields[4], 1, UINT32_MAX, &binding_epoch)
      || !parse_u64(fields[5], 0, AIOTF_DIAGNOSTIC_MAX_FRAME, &frame)
      || !parse_u64(fields[6], 0, AIOTF_DIAGNOSTIC_MAX_SLOT, &slot))
    return AIOTF_CONFIG_INVALID_PENDING_CONTEXT;

  for (size_t i = 0; i < config->pending_context_count; ++i) {
    const aiotf_pending_context_config_t *existing = &config->pending_contexts[i];
    if (existing->tag_id == tag_id && existing->frame == frame && existing->slot == slot)
      return AIOTF_CONFIG_INVALID_PENDING_CONTEXT;
  }
  config->pending_contexts[config->pending_context_count++] = (aiotf_pending_context_config_t){
      .correlation_id = correlation_id,
      .session_id = session_id,
      .tag_id = (uint32_t)tag_id,
      .binding_epoch = (uint32_t)binding_epoch,
      .frame = (uint32_t)frame,
      .slot = (uint32_t)slot,
      .reader_mode = strcmp(fields[1], "diversity") == 0 ? AIOTF_READER_MODE_DIVERSITY : AIOTF_READER_MODE_NORMAL,
  };
  return AIOTF_CONFIG_OK;
}

static bool selected_tag(const aiotf_config_t *config, uint32_t tag_id)
{
  for (size_t i = 0; i < config->tag_count; ++i) {
    if (config->tag_ids[i] == tag_id)
      return true;
  }
  return false;
}

static aiotf_config_status_t parse_config(int argc, char **argv, aiotf_config_t *config)
{
  if (argc <= 1 || argv == NULL || config == NULL)
    return AIOTF_CONFIG_INVALID_ARGUMENT;

  *config = (aiotf_config_t){
      .listen_address = AIOTF_DEFAULT_ADDRESS,
      .listen_port = AIOTF_DEFAULT_PORT,
      .timeout_ms = AIOTF_DEFAULT_TIMEOUT_MS,
      .nrf_uri = AIOTF_DEFAULT_NRF_URI,
      .nf_instance_id = AIOTF_DEFAULT_NF_INSTANCE_ID,
      .nf_address = AIOTF_DEFAULT_NF_ADDRESS,
      .mcc = AIOTF_DEFAULT_MCC,
      .mnc = AIOTF_DEFAULT_MNC,
      .aiot_area_code = AIOTF_DEFAULT_AIOT_AREA_CODE,
      .nrf_timeout_ms = AIOTF_DEFAULT_NRF_TIMEOUT_MS,
      .nrf_retry_ms = AIOTF_DEFAULT_NRF_RETRY_MS,
      .sbi_address = AIOTF_DEFAULT_SBI_ADDRESS,
      .sbi_port = AIOTF_DEFAULT_SBI_PORT,
      .trusted_af_id = AIOTF_DEFAULT_TRUSTED_AF_ID,
  };
  bool have_profile = false;
  bool have_address = false;
  bool have_port = false;
  bool have_tags = false;
  bool have_timeout = false;
  bool have_nrf_uri = false;
  bool have_nf_instance_id = false;
  bool have_nf_address = false;
  bool have_mcc = false;
  bool have_mnc = false;
  bool have_aiot_area_code = false;
  bool have_nrf_timeout = false;
  bool have_nrf_retry = false;
  bool have_sbi_address = false;
  bool have_sbi_port = false;
  bool have_trusted_af_id = false;

  for (int i = 1; i < argc; ++i) {
    if (strcmp(argv[i], "--profile") == 0) {
      if (have_profile || ++i >= argc)
        return have_profile ? AIOTF_CONFIG_DUPLICATE_OPTION : AIOTF_CONFIG_INVALID_ARGUMENT;
      config->profile = parse_profile(argv[i]);
      if (config->profile == AIOTF_PROFILE_INVALID)
        return AIOTF_CONFIG_INVALID_PROFILE;
      have_profile = true;
    } else if (strcmp(argv[i], "--listen-address") == 0) {
      if (have_address || ++i >= argc)
        return have_address ? AIOTF_CONFIG_DUPLICATE_OPTION : AIOTF_CONFIG_INVALID_ARGUMENT;
      struct in_addr address;
      if (inet_pton(AF_INET, argv[i], &address) != 1)
        return AIOTF_CONFIG_INVALID_ADDRESS;
      snprintf(config->listen_address, sizeof(config->listen_address), "%s", argv[i]);
      have_address = true;
    } else if (strcmp(argv[i], "--listen-port") == 0) {
      if (have_port || ++i >= argc)
        return have_port ? AIOTF_CONFIG_DUPLICATE_OPTION : AIOTF_CONFIG_INVALID_ARGUMENT;
      const aiotf_config_status_t status = parse_port(argv[i], &config->listen_port);
      if (status != AIOTF_CONFIG_OK)
        return status;
      have_port = true;
    } else if (strcmp(argv[i], "--tags") == 0) {
      if (have_tags || ++i >= argc)
        return have_tags ? AIOTF_CONFIG_DUPLICATE_OPTION : AIOTF_CONFIG_INVALID_ARGUMENT;
      const aiotf_config_status_t status = parse_tags(argv[i], config);
      if (status != AIOTF_CONFIG_OK)
        return status;
      have_tags = true;
    } else if (strcmp(argv[i], "--timeout-ms") == 0) {
      if (have_timeout || ++i >= argc)
        return have_timeout ? AIOTF_CONFIG_DUPLICATE_OPTION : AIOTF_CONFIG_INVALID_ARGUMENT;
      const aiotf_config_status_t status = parse_timeout(argv[i], &config->timeout_ms);
      if (status != AIOTF_CONFIG_OK)
        return status;
      have_timeout = true;
    } else if (strcmp(argv[i], "--pending-context") == 0) {
      if (++i >= argc)
        return AIOTF_CONFIG_INVALID_ARGUMENT;
      const aiotf_config_status_t status = parse_pending_context(argv[i], config);
      if (status != AIOTF_CONFIG_OK)
        return status;
    } else if (strcmp(argv[i], "--nrf-uri") == 0) {
      if (have_nrf_uri || ++i >= argc)
        return have_nrf_uri ? AIOTF_CONFIG_DUPLICATE_OPTION : AIOTF_CONFIG_INVALID_ARGUMENT;
      if (!valid_http_uri(argv[i]))
        return AIOTF_CONFIG_INVALID_NRF_URI;
      snprintf(config->nrf_uri, sizeof(config->nrf_uri), "%s", argv[i]);
      have_nrf_uri = true;
    } else if (strcmp(argv[i], "--nf-instance-id") == 0) {
      if (have_nf_instance_id || ++i >= argc)
        return have_nf_instance_id ? AIOTF_CONFIG_DUPLICATE_OPTION : AIOTF_CONFIG_INVALID_ARGUMENT;
      if (!valid_uuid(argv[i]))
        return AIOTF_CONFIG_INVALID_NF_INSTANCE_ID;
      snprintf(config->nf_instance_id, sizeof(config->nf_instance_id), "%s", argv[i]);
      have_nf_instance_id = true;
    } else if (strcmp(argv[i], "--nf-address") == 0) {
      if (have_nf_address || ++i >= argc)
        return have_nf_address ? AIOTF_CONFIG_DUPLICATE_OPTION : AIOTF_CONFIG_INVALID_ARGUMENT;
      struct in_addr address;
      if (inet_pton(AF_INET, argv[i], &address) != 1)
        return AIOTF_CONFIG_INVALID_NF_ADDRESS;
      snprintf(config->nf_address, sizeof(config->nf_address), "%s", argv[i]);
      have_nf_address = true;
    } else if (strcmp(argv[i], "--mcc") == 0) {
      if (have_mcc || ++i >= argc)
        return have_mcc ? AIOTF_CONFIG_DUPLICATE_OPTION : AIOTF_CONFIG_INVALID_ARGUMENT;
      if (!valid_digits(argv[i], 3, 3))
        return AIOTF_CONFIG_INVALID_PLMN;
      snprintf(config->mcc, sizeof(config->mcc), "%s", argv[i]);
      have_mcc = true;
    } else if (strcmp(argv[i], "--mnc") == 0) {
      if (have_mnc || ++i >= argc)
        return have_mnc ? AIOTF_CONFIG_DUPLICATE_OPTION : AIOTF_CONFIG_INVALID_ARGUMENT;
      if (!valid_digits(argv[i], 2, 3))
        return AIOTF_CONFIG_INVALID_PLMN;
      snprintf(config->mnc, sizeof(config->mnc), "%s", argv[i]);
      have_mnc = true;
    } else if (strcmp(argv[i], "--aiot-area-code") == 0) {
      if (have_aiot_area_code || ++i >= argc)
        return have_aiot_area_code ? AIOTF_CONFIG_DUPLICATE_OPTION : AIOTF_CONFIG_INVALID_ARGUMENT;
      if (!valid_aiot_area_code(argv[i]))
        return AIOTF_CONFIG_INVALID_AIOT_AREA_CODE;
      snprintf(config->aiot_area_code, sizeof(config->aiot_area_code), "%s", argv[i]);
      have_aiot_area_code = true;
    } else if (strcmp(argv[i], "--nrf-timeout-ms") == 0) {
      if (have_nrf_timeout || ++i >= argc)
        return have_nrf_timeout ? AIOTF_CONFIG_DUPLICATE_OPTION : AIOTF_CONFIG_INVALID_ARGUMENT;
      if (parse_timeout(argv[i], &config->nrf_timeout_ms) != AIOTF_CONFIG_OK || config->nrf_timeout_ms > 60000)
        return AIOTF_CONFIG_INVALID_NRF_TIMEOUT;
      have_nrf_timeout = true;
    } else if (strcmp(argv[i], "--nrf-retry-ms") == 0) {
      if (have_nrf_retry || ++i >= argc)
        return have_nrf_retry ? AIOTF_CONFIG_DUPLICATE_OPTION : AIOTF_CONFIG_INVALID_ARGUMENT;
      if (parse_timeout(argv[i], &config->nrf_retry_ms) != AIOTF_CONFIG_OK || config->nrf_retry_ms > 60000)
        return AIOTF_CONFIG_INVALID_NRF_RETRY;
      have_nrf_retry = true;
    } else if (strcmp(argv[i], "--sbi-address") == 0) {
      if (have_sbi_address || ++i >= argc)
        return have_sbi_address ? AIOTF_CONFIG_DUPLICATE_OPTION : AIOTF_CONFIG_INVALID_ARGUMENT;
      struct in_addr address;
      if (inet_pton(AF_INET, argv[i], &address) != 1)
        return AIOTF_CONFIG_INVALID_SBI_ADDRESS;
      snprintf(config->sbi_address, sizeof(config->sbi_address), "%s", argv[i]);
      have_sbi_address = true;
    } else if (strcmp(argv[i], "--sbi-port") == 0) {
      if (have_sbi_port || ++i >= argc)
        return have_sbi_port ? AIOTF_CONFIG_DUPLICATE_OPTION : AIOTF_CONFIG_INVALID_ARGUMENT;
      if (parse_port(argv[i], &config->sbi_port) != AIOTF_CONFIG_OK)
        return AIOTF_CONFIG_INVALID_SBI_PORT;
      have_sbi_port = true;
    } else if (strcmp(argv[i], "--trusted-af-id") == 0) {
      if (have_trusted_af_id || ++i >= argc)
        return have_trusted_af_id ? AIOTF_CONFIG_DUPLICATE_OPTION : AIOTF_CONFIG_INVALID_ARGUMENT;
      if (!valid_af_id(argv[i]))
        return AIOTF_CONFIG_INVALID_TRUSTED_AF_ID;
      snprintf(config->trusted_af_id, sizeof(config->trusted_af_id), "%s", argv[i]);
      have_trusted_af_id = true;
    } else {
      return AIOTF_CONFIG_INVALID_ARGUMENT;
    }
  }

  if (!have_profile || !have_tags)
    return AIOTF_CONFIG_INVALID_ARGUMENT;
  if (config->profile == AIOTF_PROFILE_THIRD_PARTY_AF_NEF)
    return AIOTF_CONFIG_PROFILE_UNAVAILABLE;
  for (size_t i = 0; i < config->pending_context_count; ++i) {
    if (!selected_tag(config, config->pending_contexts[i].tag_id))
      return AIOTF_CONFIG_INVALID_PENDING_CONTEXT;
  }
  return AIOTF_CONFIG_OK;
}

static aiotf_health_t evaluate_health(aiotf_profile_t profile, const aiotf_dependencies_t *dependencies)
{
  if (dependencies == NULL)
    return (aiotf_health_t){.reason = "missing_dependencies"};

  aiotf_health_t health = {
      .live = dependencies->event_loop_running,
      .reason = "event_loop_stopped",
  };
  if (!health.live)
    return health;
  if (!dependencies->state_initialized) {
    health.reason = "state_not_initialized";
    return health;
  }

  if (profile == AIOTF_PROFILE_EXPERIMENTAL_N6) {
    health.ready = dependencies->diagnostic_listener_bound;
    health.reason = health.ready ? "ready" : "diagnostic_listener_not_bound";
  } else if (profile == AIOTF_PROFILE_TRUSTED_AF_SBI) {
    if (!dependencies->nrf_registered)
      health.reason = "nrf_dependency_unavailable";
    else if (!dependencies->sbi_listener_bound)
      health.reason = "sbi_listener_not_bound";
    else if (!dependencies->amf_available)
      health.reason = "amf_dependency_unavailable";
    else {
      health.ready = true;
      health.reason = "ready";
    }
  } else if (profile == AIOTF_PROFILE_THIRD_PARTY_AF_NEF) {
    health.ready = dependencies->sbi_listener_bound && dependencies->nrf_registered && dependencies->amf_available
                   && dependencies->nef_available;
    health.reason = health.ready ? "ready" : "nef_dependency_unavailable";
  } else {
    health.reason = "invalid_profile";
  }
  return health;
}

static bool write_status(aiotf_profile_t profile,
                         const aiotf_health_t *health,
                         const aiotf_dependencies_t *dependencies)
{
  FILE *status = fopen(AIOTF_STATUS_PATH, "w");
  if (status == NULL)
    return false;
  const int result = fprintf(status,
                             "pid=%ld\nprofile=%s\nlive=%d\nready=%d\nreason=%s\nnrf_registered=%d\n"
                             "sbi_listener_bound=%d\namf_available=%d\nnef_available=%d\n",
                             (long)getpid(),
                             profile_name(profile),
                             health->live,
                             health->ready,
                             health->reason,
                             dependencies != NULL && dependencies->nrf_registered,
                             dependencies != NULL && dependencies->sbi_listener_bound,
                             dependencies != NULL && dependencies->amf_available,
                             dependencies != NULL && dependencies->nef_available);
  return fclose(status) == 0 && result > 0;
}

static int check_status(bool require_ready)
{
  FILE *status = fopen(AIOTF_STATUS_PATH, "r");
  if (status == NULL)
    return 1;

  long pid = 0;
  int live = 0;
  int ready = 0;
  char line[128];
  while (fgets(line, sizeof(line), status) != NULL) {
    if (sscanf(line, "pid=%ld", &pid) == 1)
      continue;
    if (sscanf(line, "live=%d", &live) == 1)
      continue;
    (void)sscanf(line, "ready=%d", &ready);
  }
  fclose(status);

  if (pid <= 0 || kill((pid_t)pid, 0) != 0 || live != 1 || (require_ready && ready != 1))
    return 1;
  printf("AIOTF_HEALTH_CHECK PASS kind=%s pid=%ld\n", require_ready ? "readiness" : "liveness", pid);
  return 0;
}

static int open_listener(const aiotf_config_t *config)
{
  const int socket_fd = socket(AF_INET, SOCK_DGRAM, 0);
  if (socket_fd < 0)
    return -1;

  const int reuse = 1;
  if (setsockopt(socket_fd, SOL_SOCKET, SO_REUSEADDR, &reuse, sizeof(reuse)) != 0) {
    close(socket_fd);
    return -1;
  }

  struct sockaddr_in address = {
      .sin_family = AF_INET,
      .sin_port = htons(config->listen_port),
  };
  if (inet_pton(AF_INET, config->listen_address, &address.sin_addr) != 1
      || bind(socket_fd, (const struct sockaddr *)&address, sizeof(address)) != 0) {
    close(socket_fd);
    return -1;
  }
  return socket_fd;
}

static int open_sbi_backend_listener(uint16_t *port)
{
  if (port == NULL)
    return -1;
  const int socket_fd = socket(AF_INET, SOCK_STREAM, 0);
  if (socket_fd < 0)
    return -1;
  const int reuse = 1;
  if (setsockopt(socket_fd, SOL_SOCKET, SO_REUSEADDR, &reuse, sizeof(reuse)) != 0) {
    close(socket_fd);
    return -1;
  }
  struct sockaddr_in address = {
      .sin_family = AF_INET,
      .sin_port = 0,
  };
  if (inet_pton(AF_INET, "127.0.0.1", &address.sin_addr) != 1
      || bind(socket_fd, (const struct sockaddr *)&address, sizeof(address)) != 0 || listen(socket_fd, 16) != 0) {
    close(socket_fd);
    return -1;
  }
  socklen_t address_size = sizeof(address);
  if (getsockname(socket_fd, (struct sockaddr *)&address, &address_size) != 0) {
    close(socket_fd);
    return -1;
  }
  *port = ntohs(address.sin_port);
  return socket_fd;
}

static pid_t start_http2_proxy(const aiotf_config_t *config, uint16_t backend_port)
{
  if (config == NULL || backend_port == 0)
    return -1;
  char frontend[96];
  char backend[64];
  if (snprintf(frontend,
               sizeof(frontend),
               "--frontend=%s,%u;no-tls",
               config->sbi_address,
               config->sbi_port)
          >= (int)sizeof(frontend)
      || snprintf(backend, sizeof(backend), "--backend=127.0.0.1,%u", backend_port) >= (int)sizeof(backend))
    return -1;
  const pid_t child = fork();
  if (child != 0)
    return child;
  char *arguments[] = {
      "nghttpx", frontend, backend, "--backend-address-family=IPv4", "--log-level=WARN", "--accesslog-file=/dev/null", NULL};
  execvp(arguments[0], arguments);
  _exit(errno == ENOENT ? 127 : 126);
}

static bool wait_for_http2_proxy(const aiotf_config_t *config, pid_t proxy_pid)
{
  if (config == NULL || proxy_pid <= 0)
    return false;
  struct sockaddr_in address = {
      .sin_family = AF_INET,
      .sin_port = htons(config->sbi_port),
  };
  const char *probe_address = strcmp(config->sbi_address, "0.0.0.0") == 0 ? "127.0.0.1" : config->sbi_address;
  if (inet_pton(AF_INET, probe_address, &address.sin_addr) != 1)
    return false;
  const struct timespec delay = {.tv_nsec = 20000000};
  for (size_t attempt = 0; attempt < 50; ++attempt) {
    int child_status = 0;
    if (waitpid(proxy_pid, &child_status, WNOHANG) == proxy_pid)
      return false;
    const int probe = socket(AF_INET, SOCK_STREAM, 0);
    if (probe >= 0) {
      const int result = connect(probe, (const struct sockaddr *)&address, sizeof(address));
      close(probe);
      if (result == 0)
        return true;
    }
    nanosleep(&delay, NULL);
  }
  return false;
}

static void stop_http2_proxy(pid_t proxy_pid)
{
  if (proxy_pid <= 0)
    return;
  (void)kill(proxy_pid, SIGTERM);
  while (waitpid(proxy_pid, NULL, 0) < 0) {
    if (errno != EINTR)
      break;
  }
}

static bool send_http_response(int connection, unsigned status, const char *reason, const char *body)
{
  if (connection < 0 || reason == NULL || body == NULL)
    return false;
  char response[AIOTF_HTTP_REQUEST_MAX + 512];
  const size_t body_size = strlen(body);
  const int response_size = snprintf(response,
                                     sizeof(response),
                                     "HTTP/1.1 %u %s\r\ncontent-type: application/json\r\ncontent-length: %zu\r\n"
                                     "connection: close\r\n\r\n%s",
                                     status,
                                     reason,
                                     body_size,
                                     body);
  return response_size > 0 && (size_t)response_size < sizeof(response)
         && write_all(connection, response, (size_t)response_size);
}

static bool parse_content_length(const char *value, size_t *content_length)
{
  uint64_t parsed = 0;
  if (!parse_u64(value, 1, AIOTF_HTTP_REQUEST_MAX, &parsed) || content_length == NULL)
    return false;
  *content_length = (size_t)parsed;
  return true;
}

static bool is_json_content_type(const char *value)
{
  static const char media_type[] = "application/json";
  if (value == NULL || strncasecmp(value, media_type, sizeof(media_type) - 1) != 0)
    return false;
  const char suffix = value[sizeof(media_type) - 1];
  return suffix == '\0' || suffix == ';' || suffix == ' ' || suffix == '\t';
}

static void handle_sbi_connection(int listener,
                                  const aiotf_config_t *config,
                                  const aiotf_binding_table_t *bindings,
                                  aiotf_inventory_context_t *inventory_context,
                                  aiotf_inventory_operation_t *operation)
{
  const int connection = accept(listener, NULL, NULL);
  if (connection < 0)
    return;
  const struct timeval timeout = {.tv_sec = 1};
  (void)setsockopt(connection, SOL_SOCKET, SO_RCVTIMEO, &timeout, sizeof(timeout));
  (void)setsockopt(connection, SOL_SOCKET, SO_SNDTIMEO, &timeout, sizeof(timeout));

  char request_buffer[AIOTF_HTTP_REQUEST_MAX + 1];
  size_t received = 0;
  char *header_end = NULL;
  while (received < AIOTF_HTTP_REQUEST_MAX) {
    const ssize_t bytes = read(connection, &request_buffer[received], AIOTF_HTTP_REQUEST_MAX - received);
    if (bytes > 0) {
      received += (size_t)bytes;
      request_buffer[received] = '\0';
      header_end = strstr(request_buffer, "\r\n\r\n");
      if (header_end != NULL)
        break;
      continue;
    }
    if (bytes < 0 && errno == EINTR)
      continue;
    break;
  }
  if (header_end == NULL) {
    (void)send_http_response(connection, 400, "Bad Request", "{\"status\":400,\"cause\":\"INVALID_HTTP\"}");
    close(connection);
    return;
  }

  char method[8];
  char path[256];
  char version[16];
  char *request_line_end = strstr(request_buffer, "\r\n");
  if (request_line_end == NULL) {
    (void)send_http_response(connection, 400, "Bad Request", "{\"status\":400,\"cause\":\"INVALID_HTTP\"}");
    close(connection);
    return;
  }
  *request_line_end = '\0';
  if (sscanf(request_buffer, "%7s %255s %15s", method, path, version) != 3 || strcmp(version, "HTTP/1.1") != 0) {
    (void)send_http_response(connection, 400, "Bad Request", "{\"status\":400,\"cause\":\"INVALID_HTTP\"}");
    close(connection);
    return;
  }

  size_t content_length = 0;
  bool saw_content_length = false;
  bool have_content_length = false;
  bool duplicate_content_length = false;
  bool saw_content_type = false;
  bool json_content = false;
  bool duplicate_content_type = false;
  bool unsupported_transfer = false;
  char *header = request_line_end + 2;
  while (header < header_end) {
    char *line_end = strstr(header, "\r\n");
    if (line_end == NULL || line_end > header_end)
      break;
    *line_end = '\0';
    if (strncasecmp(header, "content-length:", 15) == 0) {
      const char *value = header + 15;
      while (*value == ' ' || *value == '\t')
        ++value;
      duplicate_content_length = saw_content_length;
      saw_content_length = true;
      if (!duplicate_content_length)
        have_content_length = parse_content_length(value, &content_length);
    } else if (strncasecmp(header, "content-type:", 13) == 0) {
      const char *value = header + 13;
      while (*value == ' ' || *value == '\t')
        ++value;
      duplicate_content_type = saw_content_type;
      saw_content_type = true;
      if (!duplicate_content_type)
        json_content = is_json_content_type(value);
    } else if (strncasecmp(header, "transfer-encoding:", 18) == 0) {
      unsupported_transfer = true;
    }
    header = line_end + 2;
  }

  if (strcmp(path, AIOTF_NAIOTF_PATH) != 0) {
    (void)send_http_response(connection, 404, "Not Found", "{\"status\":404,\"cause\":\"RESOURCE_NOT_FOUND\"}");
    close(connection);
    return;
  }
  if (strcmp(method, "POST") != 0) {
    (void)send_http_response(connection, 405, "Method Not Allowed", "{\"status\":405,\"cause\":\"METHOD_NOT_ALLOWED\"}");
    close(connection);
    return;
  }
  if (!saw_content_length) {
    (void)send_http_response(connection, 411, "Length Required", "{\"status\":411,\"cause\":\"CONTENT_LENGTH_REQUIRED\"}");
    close(connection);
    return;
  }
  if (!have_content_length || duplicate_content_length || duplicate_content_type || unsupported_transfer) {
    (void)send_http_response(connection, 400, "Bad Request", "{\"status\":400,\"cause\":\"INVALID_HTTP\"}");
    close(connection);
    return;
  }
  if (!json_content) {
    (void)send_http_response(connection, 415, "Unsupported Media Type", "{\"status\":415,\"cause\":\"UNSUPPORTED_MEDIA_TYPE\"}");
    close(connection);
    return;
  }

  char *body = header_end + 4;
  size_t body_received = received - (size_t)(body - request_buffer);
  while (body_received < content_length && received < AIOTF_HTTP_REQUEST_MAX) {
    const ssize_t bytes = read(connection, &request_buffer[received], AIOTF_HTTP_REQUEST_MAX - received);
    if (bytes > 0) {
      received += (size_t)bytes;
      body_received += (size_t)bytes;
      continue;
    }
    if (bytes < 0 && errno == EINTR)
      continue;
    break;
  }
  if (body_received < content_length) {
    (void)send_http_response(connection, 400, "Bad Request", "{\"status\":400,\"cause\":\"INCOMPLETE_BODY\"}");
    close(connection);
    return;
  }

  aiotf_naiotf_request_t inventory_request;
  const char *parse_reason = NULL;
  if (!parse_naiotf_request(body, content_length, config, &inventory_request, &parse_reason)) {
    const bool unauthorized = parse_reason != NULL && strcmp(parse_reason, "unauthorized_af") == 0;
    char problem[256];
    snprintf(problem,
             sizeof(problem),
             "{\"status\":%u,\"cause\":\"%s\"}",
             unauthorized ? 403U : 400U,
             parse_reason == NULL ? "INVALID_REQUEST" : parse_reason);
    (void)send_http_response(connection, unauthorized ? 403 : 400, unauthorized ? "Forbidden" : "Bad Request", problem);
    printf("AIOTF_NAIOTF_REQUEST REJECT profile=trusted_af_sbi reason=%s\n",
           parse_reason == NULL ? "invalid_request" : parse_reason);
    close(connection);
    return;
  }

  const char *start_reason = NULL;
  if (!start_inventory_operation(inventory_context,
                                 bindings,
                                 config,
                                 &inventory_request,
                                 monotonic_ms(),
                                 operation,
                                 &start_reason)) {
    const bool busy = start_reason != NULL && strcmp(start_reason, "inventory_busy") == 0;
    char problem[256];
    snprintf(problem,
             sizeof(problem),
             "{\"status\":%u,\"cause\":\"%s\"}",
             busy ? 429U : 400U,
             start_reason == NULL ? "OPERATION_REJECTED" : start_reason);
    (void)send_http_response(connection, busy ? 429 : 400, busy ? "Too Many Requests" : "Bad Request", problem);
    close(connection);
    return;
  }

  char response_body[AIOTF_TRANS_ID_MAX + 32];
  snprintf(response_body, sizeof(response_body), "{\"transId\":\"%s\"}", operation->trans_id);
  (void)send_http_response(connection, 200, "OK", response_body);
  printf("AIOTF_NAIOTF_REQUEST PASS profile=trusted_af_sbi af_id=%s trans_id=%s tags=%zu timeout_ms=%u\n",
         inventory_request.af_id,
         operation->trans_id,
         operation->transaction_count,
         inventory_request.timeout_ms);
  close(connection);
}

static void handle_signal(int signal_number)
{
  (void)signal_number;
  stop_requested = 1;
}

static uint64_t monotonic_ms(void)
{
  struct timespec now;
  if (clock_gettime(CLOCK_MONOTONIC, &now) != 0)
    return 0;
  return (uint64_t)now.tv_sec * 1000 + (uint64_t)now.tv_nsec / 1000000;
}

static int base64_value(char value)
{
  if (value >= 'A' && value <= 'Z')
    return value - 'A';
  if (value >= 'a' && value <= 'z')
    return value - 'a' + 26;
  if (value >= '0' && value <= '9')
    return value - '0' + 52;
  if (value == '+')
    return 62;
  if (value == '/')
    return 63;
  return -1;
}

static bool decode_base64(const char *input, uint8_t *output, size_t output_capacity, size_t *output_size)
{
  if (input == NULL || output == NULL || output_size == NULL)
    return false;
  const size_t input_size = strlen(input);
  if (input_size == 0 || input_size % 4 != 0)
    return false;

  size_t written = 0;
  for (size_t i = 0; i < input_size; i += 4) {
    int values[4] = {0};
    size_t padding = 0;
    for (size_t j = 0; j < 4; ++j) {
      if (input[i + j] == '=') {
        if (i + 4 != input_size || j < 2)
          return false;
        ++padding;
        values[j] = 0;
      } else {
        if (padding != 0 || (values[j] = base64_value(input[i + j])) < 0)
          return false;
      }
    }
    if (padding > 2 || written > output_capacity - (3 - padding))
      return false;
    const uint32_t block = ((uint32_t)values[0] << 18) | ((uint32_t)values[1] << 12)
                           | ((uint32_t)values[2] << 6) | (uint32_t)values[3];
    output[written++] = (uint8_t)(block >> 16);
    if (padding < 2)
      output[written++] = (uint8_t)(block >> 8);
    if (padding == 0)
      output[written++] = (uint8_t)block;
  }
  *output_size = written;
  return true;
}

static bool encode_base64(const uint8_t *input, size_t input_size, char *output, size_t output_capacity)
{
  static const char alphabet[] = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
  if (input == NULL || output == NULL || output_capacity < ((input_size + 2) / 3) * 4 + 1)
    return false;

  size_t read_index = 0;
  size_t written = 0;
  while (read_index < input_size) {
    const size_t remaining = input_size - read_index;
    const uint32_t first = input[read_index++];
    const uint32_t second = remaining > 1 ? input[read_index++] : 0;
    const uint32_t third = remaining > 2 ? input[read_index++] : 0;
    const uint32_t block = (first << 16) | (second << 8) | third;
    output[written++] = alphabet[(block >> 18) & 0x3f];
    output[written++] = alphabet[(block >> 12) & 0x3f];
    output[written++] = remaining > 1 ? alphabet[(block >> 6) & 0x3f] : '=';
    output[written++] = remaining > 2 ? alphabet[block & 0x3f] : '=';
  }
  output[written] = '\0';
  return true;
}

static bool write_all(int fd, const char *buffer, size_t size)
{
  size_t written = 0;
  while (written < size) {
    const ssize_t result = write(fd, &buffer[written], size - written);
    if (result > 0) {
      written += (size_t)result;
      continue;
    }
    if (result < 0 && errno == EINTR)
      continue;
    return false;
  }
  return true;
}

static bool run_jq_inventory(const char *body, size_t body_size, char *output, size_t output_capacity)
{
  static const char filter[] =
      ". as $root | if (type == \"object\") and (.afId|type == \"string\" and length > 0 and length <= 127) "
      "and (.notifUri|type == \"string\" and length > 0 and length <= 1023) "
      "and (has(\"targetArea\")|not) and (.targetDevices|type == \"object\") "
      "and (.targetDevices|has(\"filteringInfo\")|not) and (.targetDevices.devices|type == \"array\") "
      "and ((.targetDevices.devices|length) >= 1 and (.targetDevices.devices|length) <= 61) "
      "and all(.targetDevices.devices[]; type == \"string\" and length == 8) "
      "and ((has(\"numDevices\")|not) or (.numDevices|type == \"number\" and floor == . "
      "and . == ($root.targetDevices.devices|length))) "
      "and ((has(\"timeInterval\")|not) or (.timeInterval|type == \"number\" and floor == . and . > 0 and . <= 4294967)) "
      "and ((has(\"devLocReqInd\")|not) or .devLocReqInd == true) then "
      "(([.afId, .notifUri, ((.timeInterval // 0)|tostring)] + .targetDevices.devices) | map(@base64) | join(\"\\n\")) + \"\\n\" "
      "else error(\"invalid InventoryReq\") end";
  if (body == NULL || body_size == 0 || output == NULL || output_capacity < 2)
    return false;

  int input_pipe[2] = {-1, -1};
  int output_pipe[2] = {-1, -1};
  if (pipe(input_pipe) != 0 || pipe(output_pipe) != 0) {
    if (input_pipe[0] >= 0) {
      close(input_pipe[0]);
      close(input_pipe[1]);
    }
    if (output_pipe[0] >= 0) {
      close(output_pipe[0]);
      close(output_pipe[1]);
    }
    return false;
  }
  const pid_t child = fork();
  if (child < 0) {
    close(input_pipe[0]);
    close(input_pipe[1]);
    close(output_pipe[0]);
    close(output_pipe[1]);
    return false;
  }
  if (child == 0) {
    close(input_pipe[1]);
    close(output_pipe[0]);
    const int null_fd = open("/dev/null", O_WRONLY);
    if (dup2(input_pipe[0], STDIN_FILENO) < 0 || dup2(output_pipe[1], STDOUT_FILENO) < 0 || null_fd < 0
        || dup2(null_fd, STDERR_FILENO) < 0)
      _exit(126);
    close(null_fd);
    close(input_pipe[0]);
    close(output_pipe[1]);
    char *arguments[] = {"jq", "-e", "-j", (char *)filter, NULL};
    execvp(arguments[0], arguments);
    _exit(errno == ENOENT ? 127 : 126);
  }

  close(input_pipe[0]);
  close(output_pipe[1]);
  const bool input_ok = write_all(input_pipe[1], body, body_size);
  close(input_pipe[1]);
  size_t output_size = 0;
  while (output_size + 1 < output_capacity) {
    const ssize_t bytes = read(output_pipe[0], &output[output_size], output_capacity - output_size - 1);
    if (bytes > 0) {
      output_size += (size_t)bytes;
      continue;
    }
    if (bytes < 0 && errno == EINTR)
      continue;
    break;
  }
  close(output_pipe[0]);
  int child_status = 0;
  while (waitpid(child, &child_status, 0) < 0) {
    if (errno != EINTR)
      return false;
  }
  output[output_size] = '\0';
  return input_ok && WIFEXITED(child_status) && WEXITSTATUS(child_status) == 0 && output_size > 0;
}

static bool decode_text_field(const char *encoded, char *output, size_t output_capacity)
{
  if (encoded == NULL || output == NULL || output_capacity < 2)
    return false;
  size_t output_size = 0;
  if (!decode_base64(encoded, (uint8_t *)output, output_capacity - 1, &output_size) || output_size == 0)
    return false;
  for (size_t i = 0; i < output_size; ++i) {
    if ((unsigned char)output[i] < 0x20 || (unsigned char)output[i] > 0x7e)
      return false;
  }
  output[output_size] = '\0';
  return true;
}

static bool valid_callback_uri(const char *value)
{
  if (value == NULL || strncmp(value, "http://", 7) != 0 || value[7] == '\0' || strlen(value) > AIOTF_URI_MAX)
    return false;
  for (const char *cursor = value + 7; *cursor != '\0'; ++cursor) {
    if (!isalnum((unsigned char)*cursor) && strchr(".-:/_?&=%", *cursor) == NULL)
      return false;
  }
  return true;
}

static bool parse_naiotf_request(const char *body,
                                 size_t body_size,
                                 const aiotf_config_t *config,
                                 aiotf_naiotf_request_t *request,
                                 const char **reason)
{
  if (reason != NULL)
    *reason = "invalid_request";
  if (body == NULL || config == NULL || request == NULL || reason == NULL || body_size == 0
      || body_size > AIOTF_HTTP_REQUEST_MAX)
    return false;

  char normalized[AIOTF_JSON_OUTPUT_MAX + 1];
  if (!run_jq_inventory(body, body_size, normalized, sizeof(normalized))) {
    *reason = "invalid_json_or_schema";
    return false;
  }

  *request = (aiotf_naiotf_request_t){0};
  char *fields[AIOTF_MAX_TAGS + 4] = {0};
  size_t field_count = 0;
  char *save = NULL;
  for (char *field = strtok_r(normalized, "\n", &save); field != NULL; field = strtok_r(NULL, "\n", &save)) {
    if (field_count == sizeof(fields) / sizeof(fields[0])) {
      *reason = "too_many_tags";
      return false;
    }
    fields[field_count++] = field;
  }
  if (field_count < 4 || !decode_text_field(fields[0], request->af_id, sizeof(request->af_id))
      || !decode_text_field(fields[1], request->notif_uri, sizeof(request->notif_uri))) {
    *reason = "invalid_text_field";
    return false;
  }
  if (!valid_af_id(request->af_id) || strcmp(request->af_id, config->trusted_af_id) != 0) {
    *reason = "unauthorized_af";
    return false;
  }
  if (!valid_callback_uri(request->notif_uri)) {
    *reason = "invalid_notification_uri";
    return false;
  }

  char timeout_seconds_text[24];
  uint64_t timeout_seconds = 0;
  if (!decode_text_field(fields[2], timeout_seconds_text, sizeof(timeout_seconds_text))
      || !parse_u64(timeout_seconds_text, 0, UINT32_MAX / 1000, &timeout_seconds)) {
    *reason = "invalid_time_interval";
    return false;
  }
  request->timeout_ms = timeout_seconds == 0 ? config->timeout_ms : (uint32_t)timeout_seconds * 1000;

  bool selected[AIOTF_MAX_TAGS + 1] = {false};
  request->tag_count = field_count - 3;
  if (request->tag_count == 0 || request->tag_count > AIOTF_MAX_TAGS) {
    *reason = "unsupported_tag_count";
    return false;
  }
  for (size_t i = 0; i < request->tag_count; ++i) {
    char permanent_id[16];
    uint8_t decoded_id[8];
    size_t decoded_id_size = 0;
    if (!decode_text_field(fields[i + 3], permanent_id, sizeof(permanent_id))
        || !decode_base64(permanent_id, decoded_id, sizeof(decoded_id), &decoded_id_size) || decoded_id_size != 4) {
      *reason = "invalid_device_id";
      return false;
    }
    uint32_t network_id = 0;
    memcpy(&network_id, decoded_id, sizeof(network_id));
    const uint32_t tag_id = ntohl(network_id);
    if (tag_id == 0 || tag_id > AIOTF_MAX_TAGS || selected[tag_id] || !selected_tag(config, tag_id)) {
      *reason = selected[tag_id] ? "duplicate_tag" : "unsupported_tag";
      return false;
    }
    selected[tag_id] = true;
    request->tag_ids[i] = tag_id;
  }
  *reason = "accepted";
  return true;
}

static bool start_inventory_operation(aiotf_inventory_context_t *context,
                                      const aiotf_binding_table_t *bindings,
                                      const aiotf_config_t *config,
                                      const aiotf_naiotf_request_t *request,
                                      uint64_t now_ms,
                                      aiotf_inventory_operation_t *operation,
                                      const char **reason)
{
  if (reason != NULL)
    *reason = "invalid_argument";
  if (context == NULL || bindings == NULL || config == NULL || request == NULL || operation == NULL || reason == NULL)
    return false;
  if (operation->active) {
    *reason = "inventory_busy";
    return false;
  }
  if (request->tag_count == 0 || request->tag_count > AIOTF_MAX_TAGS || request->timeout_ms == 0
      || now_ms == 0 || now_ms > UINT64_MAX - request->timeout_ms || context->next_correlation_id == 0) {
    *reason = "invalid_operation_boundary";
    return false;
  }

  aiotf_inventory_context_t next_context = *context;
  aiotf_tag_transaction_t scheduled[AIOTF_MAX_TAGS];
  size_t scheduled_count = 0;
  const uint64_t correlation_id = next_context.next_correlation_id++;
  if (aiotf_schedule_transactions(&next_context,
                                  bindings,
                                  correlation_id,
                                  request->tag_ids,
                                  request->tag_count,
                                  0,
                                  scheduled,
                                  AIOTF_MAX_TAGS,
                                  &scheduled_count)
      != AIOTF_SCHEDULE_OK) {
    *reason = "schedule_rejected";
    return false;
  }

  aiotf_inventory_operation_t candidate = {
      .active = true,
      .transaction_count = scheduled_count,
      .deadline_ms = now_ms + request->timeout_ms,
  };
  snprintf(candidate.notif_uri, sizeof(candidate.notif_uri), "%s", request->notif_uri);
  const int trans_id_length = snprintf(candidate.trans_id,
                                       sizeof(candidate.trans_id),
                                       "%s-%016llx-%llu",
                                       config->nf_instance_id,
                                       (unsigned long long)now_ms,
                                       (unsigned long long)correlation_id);
  if (trans_id_length <= 0 || (size_t)trans_id_length >= sizeof(candidate.trans_id)) {
    *reason = "transaction_id_overflow";
    return false;
  }

  for (size_t i = 0; i < scheduled_count; ++i) {
    const aiotf_reader_binding_t *binding = aiotf_binding_table_get(bindings, scheduled[i].tag_id);
    aiotf_reader_selection_t readers;
    const aiotf_reader_mode_t mode = binding != NULL && binding->eligible_reader_count > 1 ? AIOTF_READER_MODE_DIVERSITY
                                                                                           : AIOTF_READER_MODE_NORMAL;
    if (binding == NULL || aiotf_select_readers(binding, mode, true, true, &readers) != AIOTF_READER_SELECTION_OK
        || !aiotf_report_arbitration_init(&candidate.transactions[i],
                                          &scheduled[i],
                                          &readers,
                                          candidate.deadline_ms)) {
      *reason = "reader_selection_rejected";
      return false;
    }
  }

  *context = next_context;
  *operation = candidate;
  *reason = "accepted";
  return true;
}

static aiotf_arbitration_status_t inventory_operation_submit_report(aiotf_inventory_operation_t *operation,
                                                                    const aiotf_inventory_report_t *report,
                                                                    uint64_t now_ms)
{
  if (operation == NULL || report == NULL || !operation->active)
    return AIOTF_ARBITRATION_INVALID_ARGUMENT;
  for (size_t i = 0; i < operation->transaction_count; ++i) {
    aiotf_report_arbitration_t *transaction = &operation->transactions[i];
    if (transaction->transaction.correlation_id == report->correlation_id
        && transaction->transaction.session_id == report->session_id
        && transaction->transaction.tag_id == report->tag_id)
      return aiotf_arbitrate_report(transaction, report, now_ms);
  }
  return AIOTF_ARBITRATION_INVALID_CORRELATION;
}

static bool inventory_operation_finished(aiotf_inventory_operation_t *operation, uint64_t now_ms)
{
  if (operation == NULL || !operation->active)
    return false;
  bool finished = true;
  for (size_t i = 0; i < operation->transaction_count; ++i) {
    aiotf_report_arbitration_t *transaction = &operation->transactions[i];
    if (transaction->transaction.result == AIOTF_RESULT_PENDING)
      (void)aiotf_report_arbitration_expire(transaction, now_ms);
    if (transaction->transaction.result == AIOTF_RESULT_PENDING)
      finished = false;
  }
  return finished;
}

static bool append_json(char *output, size_t output_capacity, size_t *used, const char *format, ...)
{
  if (output == NULL || used == NULL || format == NULL || *used >= output_capacity)
    return false;
  va_list arguments;
  va_start(arguments, format);
  const int length = vsnprintf(&output[*used], output_capacity - *used, format, arguments);
  va_end(arguments);
  if (length < 0 || (size_t)length >= output_capacity - *used)
    return false;
  *used += (size_t)length;
  return true;
}

static bool encode_tag_permanent_id(uint32_t tag_id, char output[9])
{
  const uint32_t network_id = htonl(tag_id);
  return encode_base64((const uint8_t *)&network_id, sizeof(network_id), output, 9);
}

static bool build_inventory_notification(const aiotf_inventory_operation_t *operation,
                                         char *payload,
                                         size_t payload_capacity)
{
  if (operation == NULL || !operation->active || payload == NULL || payload_capacity == 0)
    return false;
  size_t completed = 0;
  for (size_t i = 0; i < operation->transaction_count; ++i) {
    if (operation->transactions[i].has_result)
      ++completed;
  }

  size_t used = 0;
  if (completed == 0)
    return append_json(payload,
                       payload_capacity,
                       &used,
                       "{\"transId\":\"%s\",\"lastRepInd\":true,\"failCause\":\"NO_SUCC_INV_RESP\"}",
                       operation->trans_id);
  if (!append_json(payload, payload_capacity, &used, "{\"transId\":\"%s\",\"devicesRepData\":[", operation->trans_id))
    return false;
  for (size_t i = 0; i < operation->transaction_count; ++i) {
    const aiotf_report_arbitration_t *transaction = &operation->transactions[i];
    char device_id[9];
    if (!encode_tag_permanent_id(transaction->transaction.tag_id, device_id)
        || !append_json(payload,
                        payload_capacity,
                        &used,
                        "%s{\"deviceId\":\"%s\"",
                        i == 0 ? "" : ",",
                        device_id))
      return false;
    if (transaction->has_result) {
      char report_payload[AIOTF_MAX_PAYLOAD_BYTES * 2 + 1];
      if (!encode_base64(transaction->result_report.payload,
                         transaction->result_report.payload_len,
                         report_payload,
                         sizeof(report_payload))
          || !append_json(payload, payload_capacity, &used, ",\"readCmdRep\":\"%s\"}", report_payload))
        return false;
    } else if (!append_json(payload, payload_capacity, &used, ",\"failCause\":\"ERROR_UNSPECIFIED\"}")) {
      return false;
    }
  }
  return append_json(payload, payload_capacity, &used, "],\"lastRepInd\":true}");
}

static bool notify_inventory_result(aiotf_inventory_operation_t *operation, uint32_t timeout_ms, uint64_t now_ms)
{
  if (operation == NULL || !operation->active || operation->notification_sent
      || (operation->last_notification_attempt_ms != 0 && now_ms >= operation->last_notification_attempt_ms
          && now_ms - operation->last_notification_attempt_ms < AIOTF_CALLBACK_RETRY_MS))
    return false;
  char payload[AIOTF_HTTP_REQUEST_MAX + 1];
  if (!build_inventory_notification(operation, payload, sizeof(payload)))
    return false;
  operation->last_notification_attempt_ms = now_ms;
  aiotf_http_response_t response = {0};
  const bool sent = run_curl("POST", operation->notif_uri, payload, timeout_ms, &response) && response.curl_exit == 0
                    && response.http_code == 204;
  operation->notification_sent = sent;
  printf("AIOTF_NAIOTF_NOTIFY %s profile=trusted_af_sbi trans_id=%s code=%ld curl_exit=%d\n",
         sent ? "PASS" : "REJECT",
         operation->trans_id,
         response.http_code,
         response.curl_exit);
  if (sent)
    operation->active = false;
  return sent;
}

static const char *nrf_status_reason(aiotf_nrf_status_t status)
{
  switch (status) {
    case AIOTF_NRF_OK:
      return "accepted";
    case AIOTF_NRF_HTTP_REJECTED:
      return "http_rejected";
    case AIOTF_NRF_TIMEOUT:
      return "timeout";
    case AIOTF_NRF_UNAVAILABLE:
      return "unavailable";
    case AIOTF_NRF_READBACK_REJECTED:
      return "readback_rejected";
    case AIOTF_NRF_DISCOVERY_REJECTED:
      return "discovery_rejected";
    default:
      return "internal_error";
  }
}

static bool parse_curl_output(aiotf_http_response_t *response, size_t output_size)
{
  response->body[output_size] = '\0';
  char *code_line = strrchr(response->body, '\n');
  if (code_line == NULL || strlen(code_line + 1) != 3)
    return false;
  char *end = NULL;
  errno = 0;
  const long code = strtol(code_line + 1, &end, 10);
  if (errno != 0 || end == code_line + 1 || *end != '\0' || code < 0 || code > 599)
    return false;
  *code_line = '\0';
  response->http_code = code;
  return true;
}

static bool run_curl(const char *method,
                     const char *url,
                     const char *payload,
                     uint32_t timeout_ms,
                     aiotf_http_response_t *response)
{
  if (method == NULL || url == NULL || response == NULL)
    return false;

  int output_pipe[2];
  if (pipe(output_pipe) != 0)
    return false;

  char timeout[24];
  snprintf(timeout, sizeof(timeout), "%u.%03u", timeout_ms / 1000, timeout_ms % 1000);
  const pid_t child = fork();
  if (child < 0) {
    close(output_pipe[0]);
    close(output_pipe[1]);
    return false;
  }
  if (child == 0) {
    close(output_pipe[0]);
    if (dup2(output_pipe[1], STDOUT_FILENO) < 0)
      _exit(126);
    close(output_pipe[1]);
    char *arguments[20];
    size_t count = 0;
    arguments[count++] = "curl";
    arguments[count++] = "--http2-prior-knowledge";
    arguments[count++] = "--silent";
    arguments[count++] = "--show-error";
    arguments[count++] = "--connect-timeout";
    arguments[count++] = timeout;
    arguments[count++] = "--max-time";
    arguments[count++] = timeout;
    arguments[count++] = "--request";
    arguments[count++] = (char *)method;
    if (payload != NULL) {
      arguments[count++] = "--header";
      arguments[count++] = "content-type: application/json";
      arguments[count++] = "--data-binary";
      arguments[count++] = (char *)payload;
    }
    arguments[count++] = "--write-out";
    arguments[count++] = "\n%{http_code}";
    arguments[count++] = (char *)url;
    arguments[count] = NULL;
    execvp(arguments[0], arguments);
    _exit(errno == ENOENT ? 127 : 126);
  }

  close(output_pipe[1]);
  *response = (aiotf_http_response_t){0};
  size_t output_size = 0;
  while (output_size < AIOTF_NRF_RESPONSE_MAX) {
    const ssize_t bytes = read(output_pipe[0], &response->body[output_size], AIOTF_NRF_RESPONSE_MAX - output_size);
    if (bytes > 0) {
      output_size += (size_t)bytes;
      continue;
    }
    if (bytes < 0 && errno == EINTR)
      continue;
    break;
  }
  close(output_pipe[0]);

  int child_status = 0;
  while (waitpid(child, &child_status, 0) < 0) {
    if (errno != EINTR)
      return false;
  }
  response->curl_exit = WIFEXITED(child_status) ? WEXITSTATUS(child_status) : 128;
  return parse_curl_output(response, output_size);
}

static void compact_json(char *value)
{
  char *output = value;
  for (char *cursor = value; *cursor != '\0'; ++cursor) {
    if (!isspace((unsigned char)*cursor))
      *output++ = *cursor;
  }
  *output = '\0';
}

static bool response_has_profile(aiotf_http_response_t *response, const aiotf_config_t *config)
{
  compact_json(response->body);
  char id[96];
  char area[64];
  snprintf(id, sizeof(id), "\"nfInstanceId\":\"%s\"", config->nf_instance_id);
  snprintf(area, sizeof(area), "\"aiotAreaCode\":\"%s\"", config->aiot_area_code);
  return strstr(response->body, id) != NULL && strstr(response->body, "\"nfType\":\"AIOTF\"") != NULL
         && strstr(response->body, area) != NULL;
}

static bool build_nrf_profile(const aiotf_config_t *config, char *profile, size_t profile_size)
{
  const int length = snprintf(profile,
                              profile_size,
                              "{\"nfInstanceId\":\"%s\",\"nfType\":\"AIOTF\",\"nfStatus\":\"REGISTERED\","
                              "\"heartBeatTimer\":50,\"ipv4Addresses\":[\"%s\"],\"aiotfInfoList\":{"
                              "\"primary\":{\"aiotAreaIDList\":[{\"plmnId\":{\"mcc\":\"%s\",\"mnc\":\"%s\"},"
                              "\"aiotAreaCode\":\"%s\"}]}}}",
                              config->nf_instance_id,
                              config->nf_address,
                              config->mcc,
                              config->mnc,
                              config->aiot_area_code);
  return length > 0 && (size_t)length < profile_size;
}

static aiotf_nrf_status_t classify_transport(const aiotf_http_response_t *response)
{
  if (response->curl_exit == 28)
    return AIOTF_NRF_TIMEOUT;
  if (response->curl_exit != 0)
    return AIOTF_NRF_UNAVAILABLE;
  return AIOTF_NRF_OK;
}

static aiotf_nrf_status_t register_and_verify_nrf(const aiotf_config_t *config,
                                                  bool *profile_maybe_present,
                                                  aiotf_http_response_t *last_response)
{
  char profile[AIOTF_NRF_PROFILE_MAX + 1];
  char instance_url[AIOTF_NRF_URI_MAX + AIOTF_UUID_LENGTH + 48];
  char discovery_url[AIOTF_NRF_URI_MAX + 512];
  if (!build_nrf_profile(config, profile, sizeof(profile))
      || snprintf(instance_url,
                  sizeof(instance_url),
                  "%s/nnrf-nfm/v1/nf-instances/%s",
                  config->nrf_uri,
                  config->nf_instance_id)
             >= (int)sizeof(instance_url)
      || snprintf(discovery_url,
                  sizeof(discovery_url),
                  "%s/nnrf-disc/v1/nf-instances?target-nf-type=AIOTF&requester-nf-type=AIOTF&"
                  "aiot-area-ids=%%5B%%7B%%22plmnId%%22%%3A%%7B%%22mcc%%22%%3A%%22%s%%22%%2C%%22mnc%%22%%3A%%22%s%%22%%7D%%2C"
                  "%%22aiotAreaCode%%22%%3A%%22%s%%22%%7D%%5D",
                  config->nrf_uri,
                  config->mcc,
                  config->mnc,
                  config->aiot_area_code)
             >= (int)sizeof(discovery_url))
    return AIOTF_NRF_INTERNAL_ERROR;

  if (!run_curl("PUT", instance_url, profile, config->nrf_timeout_ms, last_response))
    return AIOTF_NRF_INTERNAL_ERROR;
  aiotf_nrf_status_t transport = classify_transport(last_response);
  if (transport != AIOTF_NRF_OK)
    return transport;
  if (last_response->http_code != 200 && last_response->http_code != 201)
    return AIOTF_NRF_HTTP_REJECTED;
  *profile_maybe_present = true;
  printf("AIOTF_NRF_REGISTRATION profile=trusted_af_sbi result=accepted code=%ld instance=%s\n",
         last_response->http_code,
         config->nf_instance_id);

  if (!run_curl("GET", instance_url, NULL, config->nrf_timeout_ms, last_response))
    return AIOTF_NRF_INTERNAL_ERROR;
  transport = classify_transport(last_response);
  if (transport != AIOTF_NRF_OK)
    return transport;
  if (last_response->http_code != 200 || !response_has_profile(last_response, config))
    return AIOTF_NRF_READBACK_REJECTED;
  printf("AIOTF_NRF_READBACK profile=trusted_af_sbi result=accepted code=200 instance=%s\n",
         config->nf_instance_id);

  if (!run_curl("GET", discovery_url, NULL, config->nrf_timeout_ms, last_response))
    return AIOTF_NRF_INTERNAL_ERROR;
  transport = classify_transport(last_response);
  if (transport != AIOTF_NRF_OK)
    return transport;
  if (last_response->http_code != 200 || !response_has_profile(last_response, config))
    return AIOTF_NRF_DISCOVERY_REJECTED;
  printf("AIOTF_NRF_DISCOVERY profile=trusted_af_sbi result=accepted code=200 instance=%s area=%s\n",
         config->nf_instance_id,
         config->aiot_area_code);
  return AIOTF_NRF_OK;
}

static bool deregister_nrf(const aiotf_config_t *config)
{
  char instance_url[AIOTF_NRF_URI_MAX + AIOTF_UUID_LENGTH + 48];
  if (snprintf(instance_url,
               sizeof(instance_url),
               "%s/nnrf-nfm/v1/nf-instances/%s",
               config->nrf_uri,
               config->nf_instance_id)
      >= (int)sizeof(instance_url))
    return false;
  aiotf_http_response_t response;
  if (!run_curl("DELETE", instance_url, NULL, config->nrf_timeout_ms, &response))
    return false;
  const bool accepted = response.curl_exit == 0 && (response.http_code == 204 || response.http_code == 404);
  printf("AIOTF_NRF_DEREGISTRATION profile=trusted_af_sbi result=%s code=%ld curl_exit=%d instance=%s\n",
         accepted ? "accepted" : "rejected",
         response.http_code,
         response.curl_exit,
         config->nf_instance_id);
  return accepted;
}

static bool build_pending_contexts(const aiotf_config_t *config,
                                   const aiotf_binding_table_t *bindings,
                                   aiotf_pending_report_context_t *contexts)
{
  const uint64_t now_ms = monotonic_ms();
  if (now_ms == 0 || now_ms > UINT64_MAX - config->timeout_ms)
    return false;
  for (size_t i = 0; i < config->pending_context_count; ++i) {
    const aiotf_pending_context_config_t *pending = &config->pending_contexts[i];
    const aiotf_reader_binding_t *binding = aiotf_binding_table_get(bindings, pending->tag_id);
    if (binding == NULL || binding->binding_epoch != pending->binding_epoch)
      return false;
    for (size_t j = 0; j < i; ++j) {
      if (config->pending_contexts[j].session_id == pending->session_id)
        return false;
    }

    aiotf_reader_selection_t readers;
    if (aiotf_select_readers(binding, pending->reader_mode, true, true, &readers) != AIOTF_READER_SELECTION_OK)
      return false;
    const aiotf_tag_transaction_t transaction = {
        .correlation_id = pending->correlation_id,
        .session_id = pending->session_id,
        .response_slot = ((uint64_t)pending->frame << 32) | pending->slot,
        .tag_id = pending->tag_id,
        .binding_epoch = pending->binding_epoch,
        .result = AIOTF_RESULT_PENDING,
    };
    contexts[i] = (aiotf_pending_report_context_t){
        .frame = pending->frame,
        .slot = pending->slot,
    };
    if (!aiotf_report_arbitration_init(&contexts[i].arbitration, &transaction, &readers, now_ms + config->timeout_ms))
      return false;
  }
  return true;
}

static uint16_t wire_u16(const uint8_t *wire)
{
  uint16_t value;
  memcpy(&value, wire, sizeof(value));
  return ntohs(value);
}

static uint32_t wire_u32(const uint8_t *wire)
{
  uint32_t value;
  memcpy(&value, wire, sizeof(value));
  return ntohl(value);
}

static bool parse_diagnostic_wire(const uint8_t *wire,
                                  size_t wire_size,
                                  aiotf_diagnostic_report_t *report,
                                  const char **reason)
{
  if (reason != NULL)
    *reason = "invalid_argument";
  if (wire == NULL || report == NULL || reason == NULL)
    return false;
  if (wire_size != AIOTF_DIAGNOSTIC_WIRE_SIZE) {
    *reason = "invalid_length";
    return false;
  }
  if (wire_u32(wire) != AIOTF_DIAGNOSTIC_MAGIC) {
    *reason = "invalid_magic";
    return false;
  }
  if (wire[4] != AIOTF_DIAGNOSTIC_VERSION) {
    *reason = "invalid_version";
    return false;
  }

  const uint8_t payload_len = wire[5];
  const uint16_t flags = wire_u16(&wire[6]);
  const uint32_t reader_handle = wire_u32(&wire[8]);
  const uint32_t tag_id = wire_u32(&wire[12]);
  const uint32_t frame = wire_u32(&wire[16]);
  const uint32_t slot = wire_u32(&wire[20]);
  if (payload_len == 0 || payload_len > AIOTF_MAX_PAYLOAD_BYTES) {
    *reason = "invalid_payload_length";
    return false;
  }
  if ((flags & ~AIOTF_DIAGNOSTIC_CRC_VALID) != 0) {
    *reason = "invalid_flags";
    return false;
  }
  if ((reader_handle != AIOTF_READER_UE1 && reader_handle != AIOTF_READER_UE2) || tag_id == 0
      || tag_id > AIOTF_MAX_TAGS || frame > AIOTF_DIAGNOSTIC_MAX_FRAME || slot > AIOTF_DIAGNOSTIC_MAX_SLOT) {
    *reason = "invalid_identity_or_timing";
    return false;
  }

  *report = (aiotf_diagnostic_report_t){
      .reader_handle = reader_handle,
      .tag_id = tag_id,
      .frame = frame,
      .slot = slot,
      .crc_valid = (flags & AIOTF_DIAGNOSTIC_CRC_VALID) != 0,
      .payload_len = payload_len,
  };
  memcpy(report->payload, &wire[24], payload_len);
  *reason = "ok";
  return true;
}

static const char *diagnostic_status_reason(aiotf_diagnostic_status_t status)
{
  switch (status) {
    case AIOTF_DIAGNOSTIC_NO_PENDING_CONTEXT:
      return "no_pending_context";
    case AIOTF_DIAGNOSTIC_AMBIGUOUS_CONTEXT:
      return "ambiguous_pending_context";
    case AIOTF_DIAGNOSTIC_ARBITRATION_REJECTED:
      return "arbitration_rejected";
    default:
      return "invalid_adapter_state";
  }
}

static int run_service(const aiotf_config_t *config)
{
  aiotf_binding_table_t bindings;
  aiotf_inventory_context_t inventory_context;
  aiotf_inventory_operation_t inventory_operation = {0};
  aiotf_inventory_context_init(&inventory_context);
  if (!aiotf_binding_table_init(&bindings) || !aiotf_binding_table_validate_profile(&bindings)) {
    fprintf(stderr, "AIOTF_START_REJECT profile=%s reason=state_initialization_failed\n", profile_name(config->profile));
    return 1;
  }
  for (size_t i = 0; i < config->tag_count; ++i) {
    if (aiotf_binding_table_get(&bindings, config->tag_ids[i]) == NULL) {
      fprintf(stderr,
              "AIOTF_START_REJECT profile=%s reason=tag_not_bound tag_id=%u\n",
              profile_name(config->profile),
              config->tag_ids[i]);
      return 1;
    }
  }

  aiotf_pending_report_context_t pending_contexts[AIOTF_MAX_TAGS] = {0};
  if (!build_pending_contexts(config, &bindings, pending_contexts)) {
    fprintf(stderr, "AIOTF_START_REJECT profile=%s reason=invalid_pending_context\n", profile_name(config->profile));
    return 1;
  }

  int socket_fd = -1;
  int sbi_backend_fd = -1;
  pid_t http2_proxy_pid = -1;
  if (config->profile == AIOTF_PROFILE_EXPERIMENTAL_N6) {
    socket_fd = open_listener(config);
    if (socket_fd < 0) {
      fprintf(stderr,
              "AIOTF_START_REJECT profile=%s reason=listener_bind_failed errno=%d\n",
              profile_name(config->profile),
              errno);
      return 1;
    }
  } else if (config->profile == AIOTF_PROFILE_TRUSTED_AF_SBI) {
    uint16_t backend_port = 0;
    sbi_backend_fd = open_sbi_backend_listener(&backend_port);
    if (sbi_backend_fd < 0 || (http2_proxy_pid = start_http2_proxy(config, backend_port)) <= 0
        || !wait_for_http2_proxy(config, http2_proxy_pid)) {
      fprintf(stderr,
              "AIOTF_START_REJECT profile=trusted_af_sbi reason=sbi_listener_bind_failed errno=%d\n",
              errno);
      if (sbi_backend_fd >= 0)
        close(sbi_backend_fd);
      stop_http2_proxy(http2_proxy_pid);
      return 1;
    }
  }

  stop_requested = 0;
  signal(SIGINT, handle_signal);
  signal(SIGTERM, handle_signal);
  aiotf_dependencies_t dependencies = {
      .event_loop_running = true,
      .state_initialized = true,
      .diagnostic_listener_bound = socket_fd >= 0,
      .sbi_listener_bound = sbi_backend_fd >= 0 && http2_proxy_pid > 0,
  };
  bool profile_maybe_present = false;
  uint64_t last_nrf_attempt_ms = 0;
  if (config->profile == AIOTF_PROFILE_TRUSTED_AF_SBI) {
    aiotf_http_response_t response = {0};
    const aiotf_nrf_status_t nrf_status = register_and_verify_nrf(config, &profile_maybe_present, &response);
    dependencies.nrf_registered = nrf_status == AIOTF_NRF_OK;
    last_nrf_attempt_ms = monotonic_ms();
    printf("AIOTF_NRF_GATE %s profile=trusted_af_sbi reason=%s code=%ld curl_exit=%d instance=%s\n",
           dependencies.nrf_registered ? "PASS" : "REJECT",
           nrf_status_reason(nrf_status),
           response.http_code,
           response.curl_exit,
           config->nf_instance_id);
  }
  aiotf_health_t health = evaluate_health(config->profile, &dependencies);
  if (!write_status(config->profile, &health, &dependencies)) {
    fprintf(stderr,
            "AIOTF_START_REJECT profile=%s reason=status_write_failed errno=%d\n",
            profile_name(config->profile),
            errno);
    if (socket_fd >= 0)
      close(socket_fd);
    if (sbi_backend_fd >= 0)
      close(sbi_backend_fd);
    stop_http2_proxy(http2_proxy_pid);
    if (profile_maybe_present)
      (void)deregister_nrf(config);
    return 1;
  }

  if (config->profile == AIOTF_PROFILE_EXPERIMENTAL_N6) {
    printf("AIOTF_SERVICE_LIVE profile=%s address=%s port=%u tags=%zu\n",
           profile_name(config->profile),
           config->listen_address,
           config->listen_port,
           config->tag_count);
  } else {
    printf("AIOTF_SERVICE_LIVE profile=%s nrf_uri=%s nf_address=%s sbi_address=%s sbi_port=%u tags=%zu\n",
           profile_name(config->profile),
           config->nrf_uri,
           config->nf_address,
           config->sbi_address,
           config->sbi_port,
           config->tag_count);
    printf("AIOTF_NAIOTF_LISTENER PASS profile=trusted_af_sbi protocol=h2c path=%s\n", AIOTF_NAIOTF_PATH);
  }
  printf("AIOTF_SERVICE_READY profile=%s ready=%d reason=%s\n",
         profile_name(config->profile),
         health.ready,
         health.reason);
  for (size_t i = 0; i < config->pending_context_count; ++i) {
    const aiotf_pending_context_config_t *pending = &config->pending_contexts[i];
    printf("AIOTF_PENDING_CONTEXT profile=experimental_n6 tag_id=%u correlation=%llu session=%llu epoch=%u "
           "frame=%u slot=%u mode=%s\n",
           pending->tag_id,
           (unsigned long long)pending->correlation_id,
           (unsigned long long)pending->session_id,
           pending->binding_epoch,
           pending->frame,
           pending->slot,
           pending->reader_mode == AIOTF_READER_MODE_DIVERSITY ? "diversity" : "normal");
  }

  struct pollfd descriptors[2] = {
      {.fd = socket_fd, .events = socket_fd >= 0 ? POLLIN : 0},
      {.fd = sbi_backend_fd, .events = sbi_backend_fd >= 0 ? POLLIN : 0},
  };
  const nfds_t descriptor_count = sbi_backend_fd >= 0 ? 2 : 1;
  uint8_t buffer[2048];
  while (!stop_requested) {
    const int poll_result = poll(descriptors, descriptor_count, config->profile == AIOTF_PROFILE_TRUSTED_AF_SBI ? 100 : 500);
    if (poll_result < 0) {
      if (errno == EINTR)
        continue;
      fprintf(stderr, "AIOTF_EVENT_LOOP_REJECT profile=%s reason=poll_failed errno=%d\n", profile_name(config->profile), errno);
      break;
    }
    if (config->profile == AIOTF_PROFILE_TRUSTED_AF_SBI) {
      int proxy_status = 0;
      if (http2_proxy_pid > 0 && waitpid(http2_proxy_pid, &proxy_status, WNOHANG) == http2_proxy_pid) {
        http2_proxy_pid = -1;
        dependencies.sbi_listener_bound = false;
        health = evaluate_health(config->profile, &dependencies);
        (void)write_status(config->profile, &health, &dependencies);
        printf("AIOTF_NAIOTF_LISTENER REJECT profile=trusted_af_sbi reason=http2_proxy_stopped\n");
      }
      if (poll_result > 0 && (descriptors[1].revents & POLLIN) != 0)
        handle_sbi_connection(sbi_backend_fd, config, &bindings, &inventory_context, &inventory_operation);
      const uint64_t now_ms = monotonic_ms();
      if (inventory_operation_finished(&inventory_operation, now_ms))
        (void)notify_inventory_result(&inventory_operation, config->nrf_timeout_ms, now_ms);
      if (now_ms != 0 && now_ms >= last_nrf_attempt_ms && now_ms - last_nrf_attempt_ms >= config->nrf_retry_ms) {
        aiotf_http_response_t response = {0};
        const aiotf_nrf_status_t nrf_status = register_and_verify_nrf(config, &profile_maybe_present, &response);
        dependencies.nrf_registered = nrf_status == AIOTF_NRF_OK;
        last_nrf_attempt_ms = now_ms;
        printf("AIOTF_NRF_GATE %s profile=trusted_af_sbi reason=%s code=%ld curl_exit=%d instance=%s\n",
               dependencies.nrf_registered ? "PASS" : "REJECT",
               nrf_status_reason(nrf_status),
               response.http_code,
               response.curl_exit,
               config->nf_instance_id);
        health = evaluate_health(config->profile, &dependencies);
        if (!write_status(config->profile, &health, &dependencies)) {
          fprintf(stderr, "AIOTF_EVENT_LOOP_REJECT profile=trusted_af_sbi reason=status_write_failed errno=%d\n", errno);
          break;
        }
        printf("AIOTF_SERVICE_READY profile=trusted_af_sbi ready=%d reason=%s nrf_registered=%d\n",
               health.ready,
               health.reason,
               dependencies.nrf_registered);
      }
    } else if (poll_result > 0 && (descriptors[0].revents & POLLIN) != 0) {
      const ssize_t received = recvfrom(socket_fd, buffer, sizeof(buffer), 0, NULL, NULL);
      if (received < 0) {
        printf("AIOTF_DIAGNOSTIC_REJECT profile=experimental_n6 reason=receive_failed errno=%d\n", errno);
        continue;
      }

      aiotf_diagnostic_report_t report;
      const char *wire_reason = NULL;
      if (!parse_diagnostic_wire(buffer, (size_t)received, &report, &wire_reason)) {
        printf("AIOTF_DIAGNOSTIC_REJECT profile=experimental_n6 reason=%s bytes=%zd\n", wire_reason, received);
        continue;
      }

      size_t matched_context = SIZE_MAX;
      aiotf_arbitration_status_t arbitration_status = AIOTF_ARBITRATION_INVALID_ARGUMENT;
      const aiotf_diagnostic_status_t status = aiotf_diagnostic_associate_report(pending_contexts,
                                                                                 config->pending_context_count,
                                                                                 &report,
                                                                                 monotonic_ms(),
                                                                                 &matched_context,
                                                                                 &arbitration_status);
      if (status != AIOTF_DIAGNOSTIC_ASSOCIATED) {
        printf("AIOTF_DIAGNOSTIC_REJECT profile=experimental_n6 reason=%s tag_id=%u reader_handle=%u "
               "frame=%u slot=%u arbitration=%d\n",
               diagnostic_status_reason(status),
               report.tag_id,
               report.reader_handle,
               report.frame,
               report.slot,
               arbitration_status);
        continue;
      }

      const aiotf_tag_transaction_t *transaction = &pending_contexts[matched_context].arbitration.transaction;
      printf("AIOTF_DIAGNOSTIC_ASSOCIATED profile=experimental_n6 tag_id=%u reader_handle=%u correlation=%llu "
             "session=%llu epoch=%u frame=%u slot=%u arbitration=%d\n",
             report.tag_id,
             report.reader_handle,
             (unsigned long long)transaction->correlation_id,
             (unsigned long long)transaction->session_id,
             transaction->binding_epoch,
             report.frame,
             report.slot,
             arbitration_status);
    }
  }

  if (profile_maybe_present)
    (void)deregister_nrf(config);
  if (socket_fd >= 0)
    close(socket_fd);
  if (sbi_backend_fd >= 0)
    close(sbi_backend_fd);
  stop_http2_proxy(http2_proxy_pid);
  unlink(AIOTF_STATUS_PATH);
  printf("AIOTF_SERVICE_STOPPED profile=%s\n", profile_name(config->profile));
  return 0;
}

static int self_test(void)
{
  assert(is_json_content_type("application/json"));
  assert(is_json_content_type("APPLICATION/JSON; charset=utf-8"));
  assert(!is_json_content_type("application/jsonx"));
  assert(!is_json_content_type(NULL));

  aiotf_config_t config = {0};
  char *valid[] = {"oai-aiotf", "--profile", "experimental_n6", "--tags", "1,21,60"};
  assert(parse_config(5, valid, &config) == AIOTF_CONFIG_OK);
  assert(config.tag_count == 3 && config.tag_ids[0] == 1 && config.tag_ids[2] == 60);

  char *empty[] = {"oai-aiotf", "--profile", "experimental_n6", "--tags", ""};
  assert(parse_config(5, empty, &config) == AIOTF_CONFIG_INVALID_TAGS);
  char *zero[] = {"oai-aiotf", "--profile", "experimental_n6", "--tags", "0"};
  assert(parse_config(5, zero, &config) == AIOTF_CONFIG_INVALID_TAGS);
  char *too_high[] = {"oai-aiotf", "--profile", "experimental_n6", "--tags", "61"};
  assert(parse_config(5, too_high, &config) == AIOTF_CONFIG_INVALID_TAGS);
  char *duplicate_tag[] = {"oai-aiotf", "--profile", "experimental_n6", "--tags", "20,20"};
  assert(parse_config(5, duplicate_tag, &config) == AIOTF_CONFIG_INVALID_TAGS);
  char *duplicate_option[] = {
      "oai-aiotf", "--profile", "experimental_n6", "--profile", "experimental_n6", "--tags", "1"};
  assert(parse_config(7, duplicate_option, &config) == AIOTF_CONFIG_DUPLICATE_OPTION);
  char *trusted[] = {"oai-aiotf", "--profile", "trusted_af_sbi", "--tags", "1"};
  assert(parse_config(5, trusted, &config) == AIOTF_CONFIG_OK);
  assert(strcmp(config.nrf_uri, AIOTF_DEFAULT_NRF_URI) == 0 && valid_uuid(config.nf_instance_id));
  char *unavailable[] = {"oai-aiotf", "--profile", "third_party_af_nef", "--tags", "1"};
  assert(parse_config(5, unavailable, &config) == AIOTF_CONFIG_PROFILE_UNAVAILABLE);
  char *invalid_nrf_uri[] = {
      "oai-aiotf", "--profile", "trusted_af_sbi", "--tags", "1", "--nrf-uri", "https://oai-nrf:8080"};
  assert(parse_config(7, invalid_nrf_uri, &config) == AIOTF_CONFIG_INVALID_NRF_URI);
  char *invalid_uuid[] = {
      "oai-aiotf", "--profile", "trusted_af_sbi", "--tags", "1", "--nf-instance-id", "not-a-uuid"};
  assert(parse_config(7, invalid_uuid, &config) == AIOTF_CONFIG_INVALID_NF_INSTANCE_ID);
  char *invalid_mcc[] = {"oai-aiotf", "--profile", "trusted_af_sbi", "--tags", "1", "--mcc", "01"};
  assert(parse_config(7, invalid_mcc, &config) == AIOTF_CONFIG_INVALID_PLMN);
  char *invalid_area[] = {
      "oai-aiotf", "--profile", "trusted_af_sbi", "--tags", "1", "--aiot-area-code", "00000Z"};
  assert(parse_config(7, invalid_area, &config) == AIOTF_CONFIG_INVALID_AIOT_AREA_CODE);
  char *zero_nrf_timeout[] = {
      "oai-aiotf", "--profile", "trusted_af_sbi", "--tags", "1", "--nrf-timeout-ms", "0"};
  assert(parse_config(7, zero_nrf_timeout, &config) == AIOTF_CONFIG_INVALID_NRF_TIMEOUT);
  char *max_nrf_timeout[] = {
      "oai-aiotf", "--profile", "trusted_af_sbi", "--tags", "1", "--nrf-timeout-ms", "60000"};
  assert(parse_config(7, max_nrf_timeout, &config) == AIOTF_CONFIG_OK && config.nrf_timeout_ms == 60000);
  char *over_nrf_timeout[] = {
      "oai-aiotf", "--profile", "trusted_af_sbi", "--tags", "1", "--nrf-timeout-ms", "60001"};
  assert(parse_config(7, over_nrf_timeout, &config) == AIOTF_CONFIG_INVALID_NRF_TIMEOUT);
  char *invalid_port[] = {
      "oai-aiotf", "--profile", "experimental_n6", "--tags", "1", "--listen-port", "0"};
  assert(parse_config(7, invalid_port, &config) == AIOTF_CONFIG_INVALID_PORT);
  char *pending[] = {"oai-aiotf",
                     "--profile",
                     "experimental_n6",
                     "--tags",
                     "25",
                     "--pending-context",
                     "25:diversity:9:1:1:10:5",
                     "--timeout-ms",
                     "1000"};
  assert(parse_config(9, pending, &config) == AIOTF_CONFIG_OK);
  assert(config.pending_context_count == 1 && config.pending_contexts[0].tag_id == 25
         && config.pending_contexts[0].reader_mode == AIOTF_READER_MODE_DIVERSITY && config.timeout_ms == 1000);
  char *unselected_pending[] = {
      "oai-aiotf", "--profile", "experimental_n6", "--tags", "1", "--pending-context", "25:normal:9:1:1:10:5"};
  assert(parse_config(7, unselected_pending, &config) == AIOTF_CONFIG_INVALID_PENDING_CONTEXT);
  char *invalid_pending_frame[] = {
      "oai-aiotf", "--profile", "experimental_n6", "--tags", "25", "--pending-context", "25:normal:9:1:1:1024:5"};
  assert(parse_config(7, invalid_pending_frame, &config) == AIOTF_CONFIG_INVALID_PENDING_CONTEXT);
  char *duplicate_pending[] = {"oai-aiotf",
                               "--profile",
                               "experimental_n6",
                               "--tags",
                               "25",
                               "--pending-context",
                               "25:normal:9:1:1:10:5",
                               "--pending-context",
                               "25:normal:10:2:1:10:5"};
  assert(parse_config(9, duplicate_pending, &config) == AIOTF_CONFIG_INVALID_PENDING_CONTEXT);

  uint8_t wire[AIOTF_DIAGNOSTIC_WIRE_SIZE] = {0};
  uint32_t wire32 = htonl(AIOTF_DIAGNOSTIC_MAGIC);
  memcpy(wire, &wire32, sizeof(wire32));
  wire[4] = AIOTF_DIAGNOSTIC_VERSION;
  wire[5] = 1;
  uint16_t wire16 = htons(AIOTF_DIAGNOSTIC_CRC_VALID);
  memcpy(&wire[6], &wire16, sizeof(wire16));
  wire32 = htonl(AIOTF_READER_UE1);
  memcpy(&wire[8], &wire32, sizeof(wire32));
  wire32 = htonl(25);
  memcpy(&wire[12], &wire32, sizeof(wire32));
  wire32 = htonl(10);
  memcpy(&wire[16], &wire32, sizeof(wire32));
  wire32 = htonl(5);
  memcpy(&wire[20], &wire32, sizeof(wire32));
  wire[24] = 0x11;
  aiotf_diagnostic_report_t parsed_report;
  const char *wire_reason = NULL;
  assert(parse_diagnostic_wire(wire, sizeof(wire), &parsed_report, &wire_reason));
  assert(parsed_report.tag_id == 25 && parsed_report.frame == 10 && parsed_report.slot == 5
         && parsed_report.payload[0] == 0x11);
  assert(!parse_diagnostic_wire(wire, sizeof(wire) - 1, &parsed_report, &wire_reason)
         && strcmp(wire_reason, "invalid_length") == 0);

  const aiotf_dependencies_t diagnostic = {
      .event_loop_running = true,
      .state_initialized = true,
      .diagnostic_listener_bound = true,
  };
  const aiotf_health_t ready = evaluate_health(AIOTF_PROFILE_EXPERIMENTAL_N6, &diagnostic);
  assert(ready.live && ready.ready);
  const aiotf_health_t not_ready = evaluate_health(AIOTF_PROFILE_TRUSTED_AF_SBI, &diagnostic);
  assert(not_ready.live && !not_ready.ready && strcmp(not_ready.reason, "nrf_dependency_unavailable") == 0);
  const aiotf_dependencies_t nrf_only = {
      .event_loop_running = true,
      .state_initialized = true,
      .nrf_registered = true,
  };
  const aiotf_health_t nrf_ready = evaluate_health(AIOTF_PROFILE_TRUSTED_AF_SBI, &nrf_only);
  assert(nrf_ready.live && !nrf_ready.ready && strcmp(nrf_ready.reason, "sbi_listener_not_bound") == 0);

  char *trusted_sbi[] = {"oai-aiotf",
                         "--profile",
                         "trusted_af_sbi",
                         "--tags",
                         "1,25,60",
                         "--sbi-address",
                         "127.0.0.1",
                         "--sbi-port",
                         "38080",
                         "--trusted-af-id",
                         "af.test:1"};
  assert(parse_config(11, trusted_sbi, &config) == AIOTF_CONFIG_OK);
  assert(config.sbi_port == 38080 && strcmp(config.trusted_af_id, "af.test:1") == 0);
  char *invalid_sbi_port[] = {
      "oai-aiotf", "--profile", "trusted_af_sbi", "--tags", "1", "--sbi-port", "0"};
  assert(parse_config(7, invalid_sbi_port, &config) == AIOTF_CONFIG_INVALID_SBI_PORT);
  char *invalid_af_id[] = {
      "oai-aiotf", "--profile", "trusted_af_sbi", "--tags", "1", "--trusted-af-id", "bad id"};
  assert(parse_config(7, invalid_af_id, &config) == AIOTF_CONFIG_INVALID_TRUSTED_AF_ID);

  char *trusted_inventory[] = {"oai-aiotf", "--profile", "trusted_af_sbi", "--tags", "1,25,60"};
  assert(parse_config(5, trusted_inventory, &config) == AIOTF_CONFIG_OK);
  const char valid_inventory_json[] =
      "{\"afId\":\"trusted-af\",\"targetDevices\":{\"devices\":[\"AAAAAQ==\"]},"
      "\"timeInterval\":1,\"notifUri\":\"http://127.0.0.1:39090/callback\"}";
  aiotf_naiotf_request_t naiotf_request;
  const char *naiotf_reason = NULL;
  assert(parse_naiotf_request(valid_inventory_json,
                              strlen(valid_inventory_json),
                              &config,
                              &naiotf_request,
                              &naiotf_reason));
  assert(naiotf_request.tag_count == 1 && naiotf_request.tag_ids[0] == 1 && naiotf_request.timeout_ms == 1000);
  const char unauthorized_json[] =
      "{\"afId\":\"other-af\",\"targetDevices\":{\"devices\":[\"AAAAAQ==\"]},"
      "\"notifUri\":\"http://127.0.0.1:39090/callback\"}";
  assert(!parse_naiotf_request(unauthorized_json,
                               strlen(unauthorized_json),
                               &config,
                               &naiotf_request,
                               &naiotf_reason)
         && strcmp(naiotf_reason, "unauthorized_af") == 0);
  const char empty_inventory_json[] =
      "{\"afId\":\"trusted-af\",\"targetDevices\":{\"devices\":[]},"
      "\"notifUri\":\"http://127.0.0.1:39090/callback\"}";
  assert(!parse_naiotf_request(empty_inventory_json,
                               strlen(empty_inventory_json),
                               &config,
                               &naiotf_request,
                               &naiotf_reason));
  const char duplicate_inventory_json[] =
      "{\"afId\":\"trusted-af\",\"targetDevices\":{\"devices\":[\"AAAAAQ==\",\"AAAAAQ==\"]},"
      "\"notifUri\":\"http://127.0.0.1:39090/callback\"}";
  assert(!parse_naiotf_request(duplicate_inventory_json,
                               strlen(duplicate_inventory_json),
                               &config,
                               &naiotf_request,
                               &naiotf_reason)
         && strcmp(naiotf_reason, "duplicate_tag") == 0);

  char sixty_inventory_json[8192];
  size_t sixty_used = 0;
  assert(append_json(sixty_inventory_json,
                     sizeof(sixty_inventory_json),
                     &sixty_used,
                     "{\"afId\":\"trusted-af\",\"targetDevices\":{\"devices\":["));
  for (uint32_t tag_id = 1; tag_id <= AIOTF_MAX_TAGS; ++tag_id) {
    char device_id[9];
    assert(encode_tag_permanent_id(tag_id, device_id));
    assert(append_json(sixty_inventory_json,
                       sizeof(sixty_inventory_json),
                       &sixty_used,
                       "%s\"%s\"",
                       tag_id == 1 ? "" : ",",
                       device_id));
  }
  assert(append_json(sixty_inventory_json,
                     sizeof(sixty_inventory_json),
                     &sixty_used,
                     "]},\"notifUri\":\"http://127.0.0.1:39090/callback\"}"));
  char *all_tags[] = {"oai-aiotf",
                      "--profile",
                      "trusted_af_sbi",
                      "--tags",
                      "1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60"};
  assert(parse_config(5, all_tags, &config) == AIOTF_CONFIG_OK);
  assert(parse_naiotf_request(sixty_inventory_json,
                              strlen(sixty_inventory_json),
                              &config,
                              &naiotf_request,
                              &naiotf_reason)
         && naiotf_request.tag_count == AIOTF_MAX_TAGS && naiotf_request.tag_ids[59] == 60);
  char sixty_one_inventory_json[8300];
  snprintf(sixty_one_inventory_json,
           sizeof(sixty_one_inventory_json),
           "%.*s,\"AAAAPQ==\"]},\"notifUri\":\"http://127.0.0.1:39090/callback\"}",
           (int)(strstr(sixty_inventory_json, "]},\"notifUri") - sixty_inventory_json),
           sixty_inventory_json);
  assert(!parse_naiotf_request(sixty_one_inventory_json,
                               strlen(sixty_one_inventory_json),
                               &config,
                               &naiotf_request,
                               &naiotf_reason)
         && strcmp(naiotf_reason, "unsupported_tag_count") == 0);

  assert(parse_naiotf_request(valid_inventory_json,
                              strlen(valid_inventory_json),
                              &config,
                              &naiotf_request,
                              &naiotf_reason));
  aiotf_binding_table_t service_bindings;
  aiotf_inventory_context_t service_context;
  aiotf_inventory_operation_t operation = {0};
  assert(aiotf_binding_table_init(&service_bindings));
  aiotf_inventory_context_init(&service_context);
  assert(start_inventory_operation(&service_context,
                                   &service_bindings,
                                   &config,
                                   &naiotf_request,
                                   1000,
                                   &operation,
                                   &naiotf_reason));
  assert(operation.active && operation.transaction_count == 1 && !inventory_operation_finished(&operation, 1999));
  assert(!start_inventory_operation(&service_context,
                                    &service_bindings,
                                    &config,
                                    &naiotf_request,
                                    1001,
                                    &operation,
                                    &naiotf_reason)
         && strcmp(naiotf_reason, "inventory_busy") == 0);
  aiotf_report_arbitration_t *arbitration = &operation.transactions[0];
  aiotf_inventory_report_t operation_report = {
      .correlation_id = arbitration->transaction.correlation_id,
      .session_id = arbitration->transaction.session_id,
      .tag_id = arbitration->transaction.tag_id,
      .binding_epoch = arbitration->transaction.binding_epoch,
      .reader_handle = arbitration->readers.active_readers[0],
      .crc_valid = true,
      .payload_len = 1,
      .payload = {0x5a},
  };
  aiotf_inventory_report_t stale_report = operation_report;
  stale_report.binding_epoch = operation_report.binding_epoch + 1;
  assert(inventory_operation_submit_report(&operation, &stale_report, 1500) == AIOTF_ARBITRATION_STALE_EPOCH);
  assert(inventory_operation_submit_report(&operation, &operation_report, 1500) == AIOTF_ARBITRATION_FIRST_VALID);
  assert(inventory_operation_submit_report(&operation, &operation_report, 1501) == AIOTF_ARBITRATION_DUPLICATE);
  operation_report.payload[0] = 0xa5;
  assert(inventory_operation_submit_report(&operation, &operation_report, 1502) == AIOTF_ARBITRATION_CONFLICT);
  assert(inventory_operation_finished(&operation, 1502));
  char notification[AIOTF_HTTP_REQUEST_MAX + 1];
  assert(build_inventory_notification(&operation, notification, sizeof(notification))
         && strstr(notification, "\"devicesRepData\"") != NULL && strstr(notification, "\"readCmdRep\":\"Wg==\"") != NULL);

  aiotf_inventory_operation_t timeout_operation = {0};
  assert(start_inventory_operation(&service_context,
                                   &service_bindings,
                                   &config,
                                   &naiotf_request,
                                   2000,
                                   &timeout_operation,
                                   &naiotf_reason));
  assert(!inventory_operation_finished(&timeout_operation, 2999));
  assert(inventory_operation_finished(&timeout_operation, 3000));
  assert(build_inventory_notification(&timeout_operation, notification, sizeof(notification))
         && strstr(notification, "\"failCause\":\"NO_SUCC_INV_RESP\"") != NULL);
  aiotf_inventory_operation_t restarted_operation = {0};
  aiotf_inventory_context_t restarted_context;
  aiotf_inventory_context_init(&restarted_context);
  assert(!restarted_operation.active);
  assert(start_inventory_operation(&restarted_context,
                                   &service_bindings,
                                   &config,
                                   &naiotf_request,
                                   3001,
                                   &restarted_operation,
                                   &naiotf_reason));
  assert(strcmp(restarted_operation.trans_id, timeout_operation.trans_id) != 0);

  puts("AIOTF_SERVICE_TEST PASS");
  return 0;
}

static void usage(FILE *output)
{
  fprintf(output,
          "Usage:\n"
          "  oai-aiotf --profile experimental_n6 --tags 1[,2..60] "
          "[--listen-address IPv4] [--listen-port 1..65535] [--timeout-ms N] "
          "[--pending-context TAG:normal|diversity:CORRELATION:SESSION:EPOCH:FRAME:SLOT]...\n"
          "  oai-aiotf --profile trusted_af_sbi --tags 1[,2..60] "
          "[--nrf-uri http://HOST:PORT] [--nf-instance-id UUID] [--nf-address IPv4] "
          "[--mcc DDD] [--mnc DD|DDD] [--aiot-area-code HHHHHH] "
          "[--nrf-timeout-ms 1..60000] [--nrf-retry-ms 1..60000] "
          "[--sbi-address IPv4] [--sbi-port 1..65535] [--trusted-af-id ID]\n"
          "  oai-aiotf --check-live | --check-ready | --self-test | --help\n");
}

int main(int argc, char **argv)
{
  setvbuf(stdout, NULL, _IOLBF, 0);
  if (argc == 2 && strcmp(argv[1], "--self-test") == 0)
    return self_test();
  if (argc == 2 && strcmp(argv[1], "--check-live") == 0)
    return check_status(false);
  if (argc == 2 && strcmp(argv[1], "--check-ready") == 0)
    return check_status(true);
  if (argc == 2 && (strcmp(argv[1], "--help") == 0 || strcmp(argv[1], "-h") == 0)) {
    usage(stdout);
    return 0;
  }

  aiotf_config_t config = {0};
  const aiotf_config_status_t status = parse_config(argc, argv, &config);
  if (status != AIOTF_CONFIG_OK) {
    fprintf(stderr, "AIOTF_CONFIG_REJECT status=%d profile=%s\n", status, profile_name(config.profile));
    usage(stderr);
    return 2;
  }
  return run_service(&config);
}
