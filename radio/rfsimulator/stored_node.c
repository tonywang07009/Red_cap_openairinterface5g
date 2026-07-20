/*
* Licensed to the OpenAirInterface (OAI) Software Alliance under one or more
* contributor license agreements.  See the NOTICE file distributed with
* this work for additional information regarding copyright ownership.
* The OpenAirInterface Software Alliance licenses this file to You under
* the OAI Public License, Version 1.1  (the "License"); you may not use this file
* except in compliance with the License.
* You may obtain a copy of the License at
*
*      http://www.openairinterface.org/?page_id=698
*
* Author and copyright: Laurent Thomas, open-cells.com
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*-------------------------------------------------------------------------------
* For more information about the OpenAirInterface (OAI) Software Alliance:
*      contact@openairinterface.org
*/


#include <common/utils/simple_executable.h>
#include "PHY/CODING/coding_defs.h"

#define AIOT_MAX_PAYLOAD_BYTES 16
#define AIOT_MAX_FRAME_BITS (AIOT_MAX_PAYLOAD_BYTES * 8 + 16)
#define AIOT_MANCHESTER_CHIPS_PER_BIT 2
#define AIOT_SFS_FACTOR 1
#define AIOT_D2R_CHIPS_PER_FRAME_BIT (AIOT_MANCHESTER_CHIPS_PER_BIT * 2 * AIOT_SFS_FACTOR)
#define AIOT_RESPONSE_TIMEOUT_MS 100
#define AIOT_INVENTORY_COMMAND 0x01
#define AIOT_RFSIM_MAX_SAMPLES (1U << 20)

typedef enum {
  AIOT_RESULT_OK,
  AIOT_RESULT_INVALID_LINE_CODE,
  AIOT_RESULT_CRC_FAILURE,
  AIOT_RESULT_CW_ABSENT,
  AIOT_RESULT_READER_ASLEEP,
  AIOT_RESULT_PAYLOAD_LENGTH,
  AIOT_RESULT_TIMEOUT,
} aiot_result_t;

typedef enum {
  AIOT_FAULT_NONE,
  AIOT_FAULT_INVALID_00,
  AIOT_FAULT_INVALID_11,
  AIOT_FAULT_CRC,
  AIOT_FAULT_TIMEOUT,
} aiot_fault_t;

typedef struct {
  bool cw_present;
  bool reader_awake;
  uint32_t elapsed_ms;
} aiot_tag_state_t;

static size_t aiot_crc_length_bits(size_t payload_len)
{
  return payload_len * 8 <= 24 ? 6 : 16;
}

static uint32_t aiot_crc(const uint8_t *payload, size_t payload_len)
{
  return aiot_crc_length_bits(payload_len) == 6 ? crc6((uint8_t *)payload, payload_len * 8) >> 26
                                                : crc16((uint8_t *)payload, payload_len * 8) >> 16;
}

static void aiot_encode_pair(uint8_t bit, uint8_t *pair)
{
  pair[0] = bit ? 0 : 1;
  pair[1] = bit ? 1 : 0;
}

static bool aiot_decode_pair(const uint8_t *pair, uint8_t *bit)
{
  if (pair[0] == 1 && pair[1] == 0) {
    *bit = 0;
    return true;
  }
  if (pair[0] == 0 && pair[1] == 1) {
    *bit = 1;
    return true;
  }
  return false;
}

static void aiot_encode_frame_bit(uint8_t bit, uint8_t *chips)
{
  uint8_t line_pair[2];
  aiot_encode_pair(bit, line_pair);
  aiot_encode_pair(line_pair[0], chips);
  aiot_encode_pair(line_pair[1], chips + 2);
}

static aiot_result_t aiot_encode_frame(const uint8_t *payload,
                                       size_t payload_len,
                                       bool apply_sfs,
                                       uint8_t *chips,
                                       size_t chips_capacity,
                                       size_t *chips_len)
{
  if (payload_len == 0 || payload_len > AIOT_MAX_PAYLOAD_BYTES)
    return AIOT_RESULT_PAYLOAD_LENGTH;

  const size_t payload_bits = payload_len * 8;
  const size_t crc_bits = aiot_crc_length_bits(payload_len);
  const size_t frame_bits = payload_bits + crc_bits;
  const size_t chips_per_bit = apply_sfs ? AIOT_D2R_CHIPS_PER_FRAME_BIT : AIOT_MANCHESTER_CHIPS_PER_BIT;
  const size_t required_chips = frame_bits * chips_per_bit;
  if (chips_capacity < required_chips)
    return AIOT_RESULT_PAYLOAD_LENGTH;

  const uint32_t crc = aiot_crc(payload, payload_len);
  for (size_t i = 0; i < frame_bits; ++i) {
    const uint8_t bit = i < payload_bits ? (payload[i / 8] >> (7 - i % 8)) & 1
                                         : (crc >> (crc_bits - 1 - (i - payload_bits))) & 1;
    if (apply_sfs)
      aiot_encode_frame_bit(bit, chips + i * chips_per_bit);
    else
      aiot_encode_pair(bit, chips + i * chips_per_bit);
  }
  *chips_len = required_chips;
  return AIOT_RESULT_OK;
}

static aiot_result_t aiot_decode_frame(const uint8_t *chips,
                                       size_t chips_len,
                                       size_t payload_len,
                                       bool apply_sfs,
                                       bool cw_required,
                                       bool cw_present,
                                       uint8_t *payload)
{
  if (payload_len == 0 || payload_len > AIOT_MAX_PAYLOAD_BYTES)
    return AIOT_RESULT_PAYLOAD_LENGTH;
  if (cw_required && !cw_present)
    return AIOT_RESULT_CW_ABSENT;

  const size_t payload_bits = payload_len * 8;
  const size_t crc_bits = aiot_crc_length_bits(payload_len);
  const size_t frame_bits = payload_bits + crc_bits;
  const size_t chips_per_bit = apply_sfs ? AIOT_D2R_CHIPS_PER_FRAME_BIT : AIOT_MANCHESTER_CHIPS_PER_BIT;
  if (chips_len != frame_bits * chips_per_bit)
    return AIOT_RESULT_PAYLOAD_LENGTH;

  uint8_t frame[AIOT_MAX_FRAME_BITS] = {0};
  for (size_t i = 0; i < frame_bits; ++i) {
    const uint8_t *encoded = chips + i * chips_per_bit;
    if (!apply_sfs) {
      if (!aiot_decode_pair(encoded, &frame[i]))
        return AIOT_RESULT_INVALID_LINE_CODE;
      continue;
    }

    uint8_t line_pair[2];
    if (!aiot_decode_pair(encoded, &line_pair[0]) || !aiot_decode_pair(encoded + 2, &line_pair[1])
        || !aiot_decode_pair(line_pair, &frame[i]))
      return AIOT_RESULT_INVALID_LINE_CODE;
  }

  memset(payload, 0, payload_len);
  for (size_t i = 0; i < payload_bits; ++i)
    payload[i / 8] |= frame[i] << (7 - i % 8);

  uint32_t received_crc = 0;
  for (size_t i = 0; i < crc_bits; ++i)
    received_crc = (received_crc << 1) | frame[payload_bits + i];
  return received_crc == aiot_crc(payload, payload_len) ? AIOT_RESULT_OK : AIOT_RESULT_CRC_FAILURE;
}

static void aiot_apply_fault(uint8_t *chips, size_t chips_len, aiot_fault_t fault)
{
  if (fault == AIOT_FAULT_INVALID_00) {
    aiot_encode_pair(0, chips);
    aiot_encode_pair(0, chips + 2);
  } else if (fault == AIOT_FAULT_INVALID_11) {
    aiot_encode_pair(1, chips);
    aiot_encode_pair(1, chips + 2);
  } else if (fault == AIOT_FAULT_CRC) {
    for (size_t i = chips_len - AIOT_D2R_CHIPS_PER_FRAME_BIT; i < chips_len; ++i)
      chips[i] ^= 1;
  }
}

static aiot_result_t aiot_tag_exchange(const aiot_tag_state_t *state,
                                       const uint8_t *inventory,
                                       size_t inventory_len,
                                       aiot_fault_t fault,
                                       uint8_t *decoded_inventory)
{
  if (inventory_len == 0 || inventory_len > AIOT_MAX_PAYLOAD_BYTES)
    return AIOT_RESULT_PAYLOAD_LENGTH;
  if (!state->reader_awake)
    return AIOT_RESULT_READER_ASLEEP;

  const uint8_t command[] = {AIOT_INVENTORY_COMMAND};
  uint8_t chips[AIOT_MAX_FRAME_BITS * AIOT_D2R_CHIPS_PER_FRAME_BIT];
  size_t chips_len = 0;
  aiot_result_t result = aiot_encode_frame(command, sizeof(command), false, chips, sizeof(chips), &chips_len);
  if (result != AIOT_RESULT_OK)
    return result;

  uint8_t decoded_command[sizeof(command)];
  result = aiot_decode_frame(chips, chips_len, sizeof(command), false, false, state->cw_present, decoded_command);
  if (result != AIOT_RESULT_OK || decoded_command[0] != AIOT_INVENTORY_COMMAND)
    return result == AIOT_RESULT_OK ? AIOT_RESULT_INVALID_LINE_CODE : result;
  if (fault == AIOT_FAULT_TIMEOUT || state->elapsed_ms >= AIOT_RESPONSE_TIMEOUT_MS)
    return AIOT_RESULT_TIMEOUT;

  result = aiot_encode_frame(inventory, inventory_len, true, chips, sizeof(chips), &chips_len);
  if (result != AIOT_RESULT_OK)
    return result;
  aiot_apply_fault(chips, chips_len, fault);
  return aiot_decode_frame(chips, chips_len, inventory_len, true, true, state->cw_present, decoded_inventory);
}

static int aiot_hex_nibble(char value)
{
  if (value >= '0' && value <= '9')
    return value - '0';
  if (value >= 'a' && value <= 'f')
    return value - 'a' + 10;
  if (value >= 'A' && value <= 'F')
    return value - 'A' + 10;
  return -1;
}

static bool aiot_parse_hex(const char *text, uint8_t *payload, size_t *payload_len)
{
  const size_t text_len = strlen(text);
  if (text_len == 0 || text_len % 2 != 0 || text_len / 2 > AIOT_MAX_PAYLOAD_BYTES)
    return false;
  *payload_len = text_len / 2;
  for (size_t i = 0; i < *payload_len; ++i) {
    const int high = aiot_hex_nibble(text[2 * i]);
    const int low = aiot_hex_nibble(text[2 * i + 1]);
    if (high < 0 || low < 0)
      return false;
    payload[i] = high << 4 | low;
  }
  return true;
}

static aiot_fault_t aiot_parse_fault(const char *text, bool *valid)
{
  *valid = true;
  if (strcmp(text, "none") == 0)
    return AIOT_FAULT_NONE;
  if (strcmp(text, "invalid00") == 0)
    return AIOT_FAULT_INVALID_00;
  if (strcmp(text, "invalid11") == 0)
    return AIOT_FAULT_INVALID_11;
  if (strcmp(text, "crc") == 0)
    return AIOT_FAULT_CRC;
  if (strcmp(text, "timeout") == 0)
    return AIOT_FAULT_TIMEOUT;
  *valid = false;
  return AIOT_FAULT_NONE;
}

static int aiot_tag_cli(int argc, char **argv)
{
  if (argc != 6) {
    fprintf(stderr,
            "Usage: %s --aiot-tag <cw:on|off> <reader:awake|asleep> "
            "<none|invalid00|invalid11|crc|timeout> <inventory-hex>\n",
            argv[0]);
    return 2;
  }

  aiot_tag_state_t state = {
      .cw_present = strcmp(argv[2], "cw:on") == 0,
      .reader_awake = strcmp(argv[3], "reader:awake") == 0,
      .elapsed_ms = 0,
  };
  if ((!state.cw_present && strcmp(argv[2], "cw:off") != 0)
      || (!state.reader_awake && strcmp(argv[3], "reader:asleep") != 0)) {
    fprintf(stderr, "AIOT_T2_ARGUMENT_REJECT\n");
    return 2;
  }

  bool fault_valid = false;
  const aiot_fault_t fault = aiot_parse_fault(argv[4], &fault_valid);
  uint8_t inventory[AIOT_MAX_PAYLOAD_BYTES];
  size_t inventory_len = 0;
  const size_t inventory_hex_len = strlen(argv[5]);
  if (inventory_hex_len == 0 || inventory_hex_len / 2 > AIOT_MAX_PAYLOAD_BYTES) {
    printf("AIOT_T2_LENGTH_REJECT\n");
    return 1;
  }
  if (!fault_valid || !aiot_parse_hex(argv[5], inventory, &inventory_len)) {
    fprintf(stderr, "AIOT_T2_ARGUMENT_REJECT\n");
    return 2;
  }

  uint8_t decoded_inventory[AIOT_MAX_PAYLOAD_BYTES];
  printf("AIOT_T2_CW state=%s\n", state.cw_present ? "on" : "off");
  printf("AIOT_T2_D2R_PROFILE modulation=OOK sfs=%d experimental_manchester=true\n", AIOT_SFS_FACTOR);
  const aiot_result_t result = aiot_tag_exchange(&state, inventory, inventory_len, fault, decoded_inventory);
  if (result == AIOT_RESULT_OK) {
    printf("AIOT_T2_R2D_ACCEPT\nAIOT_T2_D2R_CRC_OK\nAIOT_T2_ROUNDTRIP_OK payload=");
    for (size_t i = 0; i < inventory_len; ++i)
      printf("%02x", decoded_inventory[i]);
    printf("\n");
    return 0;
  }
  if (result == AIOT_RESULT_INVALID_LINE_CODE)
    printf("AIOT_T2_LINECODE_REJECT pair=%s\n", fault == AIOT_FAULT_INVALID_11 ? "11" : "00");
  else if (result == AIOT_RESULT_CRC_FAILURE)
    printf("AIOT_T2_CRC_REJECT\n");
  else if (result == AIOT_RESULT_CW_ABSENT)
    printf("AIOT_T2_CW_REJECT state=off\n");
  else if (result == AIOT_RESULT_READER_ASLEEP)
    printf("AIOT_T2_R2D_REJECT reason=reader_asleep\n");
  else if (result == AIOT_RESULT_PAYLOAD_LENGTH)
    printf("AIOT_T2_LENGTH_REJECT\n");
  else if (result == AIOT_RESULT_TIMEOUT)
    printf("AIOT_T2_TIMEOUT timeout_ms=%d\n", AIOT_RESPONSE_TIMEOUT_MS);
  return 1;
}

static bool aiot_expect(aiot_result_t expected,
                        const aiot_tag_state_t *state,
                        const uint8_t *inventory,
                        size_t inventory_len,
                        aiot_fault_t fault)
{
  uint8_t decoded[AIOT_MAX_PAYLOAD_BYTES];
  return aiot_tag_exchange(state, inventory, inventory_len, fault, decoded) == expected
         && (expected != AIOT_RESULT_OK || memcmp(decoded, inventory, inventory_len) == 0);
}

static int aiot_tag_self_test(void)
{
  crcTableInit();
  const aiot_tag_state_t ready = {.cw_present = true, .reader_awake = true, .elapsed_ms = 0};
  const aiot_tag_state_t cw_off = {.cw_present = false, .reader_awake = true, .elapsed_ms = 0};
  const aiot_tag_state_t asleep = {.cw_present = true, .reader_awake = false, .elapsed_ms = 0};
  const aiot_tag_state_t late = {.cw_present = true, .reader_awake = true, .elapsed_ms = AIOT_RESPONSE_TIMEOUT_MS};
  const uint8_t one_byte[] = {0xa5};
  const uint8_t max_payload[AIOT_MAX_PAYLOAD_BYTES] = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15};
  const uint8_t too_long[AIOT_MAX_PAYLOAD_BYTES + 1] = {0};
  uint8_t direction_chips[AIOT_MAX_FRAME_BITS * AIOT_D2R_CHIPS_PER_FRAME_BIT];
  size_t r2d_chips_len = 0;
  size_t d2r_chips_len = 0;
  const c16_t cw_samples[2] = {{.r = 100, .i = -50}, {.r = 100, .i = -50}};
  const uint8_t ook_chips[2] = {1, 0};
  c16_t reflected[2] = {0};
  for (size_t i = 0; i < sizeofArray(ook_chips); ++i) {
    reflected[i].r = cw_samples[i].r * ook_chips[i];
    reflected[i].i = cw_samples[i].i * ook_chips[i];
  }

  const bool passed = aiot_encode_frame(one_byte, sizeof(one_byte), false, direction_chips, sizeof(direction_chips), &r2d_chips_len)
                          == AIOT_RESULT_OK
                      && aiot_encode_frame(
                             one_byte, sizeof(one_byte), true, direction_chips, sizeof(direction_chips), &d2r_chips_len)
                             == AIOT_RESULT_OK
                      && d2r_chips_len == r2d_chips_len * 2
                      && aiot_expect(AIOT_RESULT_OK, &ready, one_byte, sizeof(one_byte), AIOT_FAULT_NONE)
                      && aiot_expect(AIOT_RESULT_OK, &ready, max_payload, sizeof(max_payload), AIOT_FAULT_NONE)
                      && aiot_expect(AIOT_RESULT_INVALID_LINE_CODE, &ready, one_byte, sizeof(one_byte), AIOT_FAULT_INVALID_00)
                      && aiot_expect(AIOT_RESULT_INVALID_LINE_CODE, &ready, one_byte, sizeof(one_byte), AIOT_FAULT_INVALID_11)
                      && aiot_expect(AIOT_RESULT_CRC_FAILURE, &ready, one_byte, sizeof(one_byte), AIOT_FAULT_CRC)
                      && aiot_expect(AIOT_RESULT_CW_ABSENT, &cw_off, one_byte, sizeof(one_byte), AIOT_FAULT_NONE)
                      && aiot_expect(AIOT_RESULT_READER_ASLEEP, &asleep, one_byte, sizeof(one_byte), AIOT_FAULT_NONE)
                      && aiot_expect(AIOT_RESULT_PAYLOAD_LENGTH, &ready, one_byte, 0, AIOT_FAULT_NONE)
                      && aiot_expect(AIOT_RESULT_PAYLOAD_LENGTH, &ready, too_long, sizeof(too_long), AIOT_FAULT_NONE)
                      && aiot_expect(AIOT_RESULT_TIMEOUT, &late, one_byte, sizeof(one_byte), AIOT_FAULT_NONE)
                      && aiot_expect(AIOT_RESULT_TIMEOUT, &ready, one_byte, sizeof(one_byte), AIOT_FAULT_TIMEOUT)
                      && reflected[0].r == cw_samples[0].r && reflected[0].i == cw_samples[0].i
                      && reflected[1].r == 0 && reflected[1].i == 0;
  printf("AIOT_T2_SELF_TEST %s\n", passed ? "PASS" : "FAIL");
  return passed ? 0 : 1;
}

volatile int             oai_exit = 0;

int fullread(int fd, void *_buf, int count) {
  char *buf = _buf;
  int ret = 0;
  int l;

  while (count) {
    l = read(fd, buf, count);

    if (l <= 0)
      return -1;

    count -= l;
    buf += l;
    ret += l;
  }

  return ret;
}

void fullwrite(int fd, void *_buf, int count) {
  char *buf = _buf;
  int l;

  while (count) {
    l = write(fd, buf, count);

    if (l <= 0) {
      if (errno==EINTR)
        continue;

      if(errno==EAGAIN) {
        continue;
      } else {
        AssertFatal(false,"Lost socket\n");
      }
    } else {
      count -= l;
      buf += l;
    }
  }
}

int server_start(short port) {
  int listen_sock;
  AssertFatal((listen_sock = socket(AF_INET, SOCK_STREAM, 0)) >= 0, "");
  int enable = 1;
  AssertFatal(setsockopt(listen_sock, SOL_SOCKET, SO_REUSEADDR, &enable, sizeof(int)) == 0, "");
  struct sockaddr_in addr = {
sin_family:
    AF_INET,
sin_port:
    htons(port),
sin_addr:
    { s_addr: INADDR_ANY }
  };
  bind(listen_sock, (struct sockaddr *)&addr, sizeof(addr));
  AssertFatal(listen(listen_sock, 5) == 0, "");
  return accept(listen_sock,NULL,NULL);
}

int client_start(char *IP, short port) {
  int sock;
  AssertFatal((sock = socket(AF_INET, SOCK_STREAM, 0)) >= 0, "");
  struct sockaddr_in addr = {
sin_family:
    AF_INET,
sin_port:
    htons(port),
sin_addr:
    { s_addr: INADDR_ANY }
  };
  addr.sin_addr.s_addr = inet_addr(IP);
  bool connected=false;

  while(!connected) {
    //LOG_I(HW,"rfsimulator: trying to connect to %s:%d\n", IP, port);
    if (connect(sock, (struct sockaddr *)&addr, sizeof(addr)) == 0) {
      //LOG_I(HW,"rfsimulator: connection established\n");
      connected=true;
    }

    perror("simulated node");
    sleep(1);
  }

  return sock;
}

enum  blocking_t {
  notBlocking,
  blocking
};

void setblocking(int sock, enum blocking_t active) {
  int opts;
  AssertFatal( (opts = fcntl(sock, F_GETFL)) >= 0,"");

  if (active==blocking)
    opts = opts & ~O_NONBLOCK;
  else
    opts = opts | O_NONBLOCK;

  AssertFatal(fcntl(sock, F_SETFL, opts) >= 0, "");
}

static bool aiot_read_exact(int fd, void *buffer, size_t count)
{
  uint8_t *cursor = buffer;
  while (count > 0) {
    const ssize_t received = read(fd, cursor, count);
    if (received == 0)
      return false;
    if (received < 0) {
      if (errno == EINTR)
        continue;
      return false;
    }
    cursor += received;
    count -= received;
  }
  return true;
}

static bool aiot_read_rfsim_packet(int fd, samplesBlockHeader_t *header, c16_t **samples, size_t *capacity)
{
  if (!aiot_read_exact(fd, header, sizeof(*header)) || header->size == 0 || header->nbAnt == 0
      || header->size > AIOT_RFSIM_MAX_SAMPLES || header->nbAnt > 64)
    return false;

  const size_t sample_count = (size_t)header->size * header->nbAnt;
  if (sample_count > AIOT_RFSIM_MAX_SAMPLES || sample_count > SIZE_MAX / sizeof(**samples))
    return false;
  if (*capacity < sample_count) {
    c16_t *resized = realloc(*samples, sample_count * sizeof(*resized));
    if (resized == NULL)
      return false;
    *samples = resized;
    *capacity = sample_count;
  }
  return aiot_read_exact(fd, *samples, sample_count * sizeof(**samples));
}

static bool aiot_parse_u32(const char *text, uint32_t minimum, uint32_t maximum, uint32_t *value)
{
  char *end = NULL;
  errno = 0;
  const unsigned long parsed = strtoul(text, &end, 10);
  if (errno != 0 || end == text || *end != '\0' || parsed < minimum || parsed > maximum)
    return false;
  *value = parsed;
  return true;
}

static bool aiot_samples_to_chips(const c16_t *samples, size_t sample_count, uint8_t *chips)
{
  if (samples == NULL || chips == NULL || sample_count == 0 || sample_count > AIOT_T2_MAX_RF_SAMPLES)
    return false;
  for (size_t i = 0; i < sample_count; ++i)
    chips[i] = samples[i].r != 0 || samples[i].i != 0;
  return true;
}

static bool aiot_d2r_payload_length(size_t chips_len, size_t *payload_len)
{
  if (chips_len == 0 || chips_len % AIOT_D2R_CHIPS_PER_FRAME_BIT != 0)
    return false;
  const size_t frame_bits = chips_len / AIOT_D2R_CHIPS_PER_FRAME_BIT;
  const size_t crc_bits = frame_bits <= 30 ? 6 : 16;
  if (frame_bits <= crc_bits || (frame_bits - crc_bits) % 8 != 0)
    return false;
  *payload_len = (frame_bits - crc_bits) / 8;
  return *payload_len > 0 && *payload_len <= AIOT_MAX_PAYLOAD_BYTES;
}

static void aiot_write_rfsim_packet(int fd, const samplesBlockHeader_t *header, const c16_t *samples)
{
  fullwrite(fd, (void *)header, sizeof(*header));
  fullwrite(fd, (void *)samples, header->size * header->nbAnt * sizeof(*samples));
}

static int aiot_cw_rfsim_cli(int argc, char **argv)
{
  if (argc != 6) {
    fprintf(stderr, "Usage: %s --aiot-cw-rfsim <server> <port> <samples> <amplitude>\n", argv[0]);
    return 2;
  }

  uint32_t port = 0;
  uint32_t sample_count = 0;
  uint32_t amplitude = 0;
  if (!aiot_parse_u32(argv[3], 1, UINT16_MAX, &port)
      || !aiot_parse_u32(argv[4], 1, AIOT_RFSIM_MAX_SAMPLES, &sample_count)
      || !aiot_parse_u32(argv[5], 1, INT16_MAX, &amplitude)) {
    fprintf(stderr, "AIOT_T2_ARGUMENT_REJECT\n");
    return 2;
  }

  const int socket = client_start(argv[2], port);
  setblocking(socket, blocking);
  samplesBlockHeader_t sync_header;
  c16_t *sync_samples = NULL;
  size_t sync_capacity = 0;
  if (!aiot_read_rfsim_packet(socket, &sync_header, &sync_samples, &sync_capacity)) {
    free(sync_samples);
    fprintf(stderr, "AIOT_T2_RFSIM_SYNC_REJECT\n");
    return 1;
  }
  free(sync_samples);

  c16_t *cw = calloc(sample_count, sizeof(*cw));
  if (cw == NULL)
    return 1;
  for (size_t i = 0; i < sample_count; ++i)
    cw[i].r = amplitude;
  const samplesBlockHeader_t header = {
      .size = sample_count,
      .nbAnt = 1,
      .timestamp = sync_header.timestamp + sync_header.size,
      .option_value = 0,
      .option_flag = OPTION_AIOT_T2_CW,
      .beam_map = 1,
  };
  aiot_write_rfsim_packet(socket, &header, cw);
  printf("AIOT_T2_CW_SOURCE samples=%u amplitude=%u\n", sample_count, amplitude);
  free(cw);
  close(socket);
  return 0;
}

static int aiot_tag_rfsim_cli(int argc, char **argv)
{
  if (argc != 6) {
    fprintf(stderr, "Usage: %s --aiot-tag-rfsim <server> <port> <tag-id> <inventory-hex>\n", argv[0]);
    return 2;
  }

  uint32_t port = 0;
  uint32_t tag_id = 0;
  uint8_t inventory[AIOT_MAX_PAYLOAD_BYTES];
  size_t inventory_len = 0;
  if (!aiot_parse_u32(argv[3], 1, UINT16_MAX, &port) || !aiot_parse_u32(argv[4], 1, 60, &tag_id)
      || !aiot_parse_hex(argv[5], inventory, &inventory_len)) {
    fprintf(stderr, "AIOT_T2_ARGUMENT_REJECT\n");
    return 2;
  }

  uint8_t chips[AIOT_MAX_FRAME_BITS * AIOT_D2R_CHIPS_PER_FRAME_BIT];
  size_t chips_len = 0;
  if (aiot_encode_frame(inventory, inventory_len, true, chips, sizeof(chips), &chips_len) != AIOT_RESULT_OK)
    return 1;

  const int socket = client_start(argv[2], port);
  setblocking(socket, blocking);
  samplesBlockHeader_t header;
  c16_t *samples = NULL;
  size_t capacity = 0;
  if (!aiot_read_rfsim_packet(socket, &header, &samples, &capacity)) {
    free(samples);
    fprintf(stderr, "AIOT_T2_RFSIM_SYNC_REJECT\n");
    return 1;
  }

  const c16_t registration_sample = {0};
  const samplesBlockHeader_t registration = {
      .size = 1,
      .nbAnt = 1,
      .timestamp = header.timestamp + header.size,
      .option_value = tag_id,
      .option_flag = OPTION_AIOT_T2_TAG_REGISTER,
      .beam_map = 1,
  };
  aiot_write_rfsim_packet(socket, &registration, &registration_sample);
  printf("AIOT_T2_TAG_REGISTER_SENT tag_id=%u\n", tag_id);

  c16_t cw[AIOT_T2_MAX_RF_SAMPLES];
  size_t cw_samples = 0;
  uint64_t cw_timestamp = 0;
  bool r2d_received = false;
  uint64_t r2d_timestamp = 0;
  while (aiot_read_rfsim_packet(socket, &header, &samples, &capacity)) {
    if (header.option_flag & OPTION_AIOT_T2_CW) {
      if (header.nbAnt != 1 || header.size < chips_len) {
        fprintf(stderr, "AIOT_T2_CW_REJECT reason=short_block samples=%u required=%zu\n", header.size, chips_len);
        continue;
      }
      memcpy(cw, samples, chips_len * sizeof(*cw));
      cw_samples = chips_len;
      cw_timestamp = header.timestamp;
      printf("AIOT_T2_CW_CAPTURE samples=%zu\n", cw_samples);
    }

    if ((header.option_flag & OPTION_AIOT_T2_R2D) && header.option_value == tag_id) {
      uint8_t r2d_chips[AIOT_T2_MAX_RF_SAMPLES];
      uint8_t command = 0;
      if (header.nbAnt != 1 || !aiot_samples_to_chips(samples, header.size, r2d_chips)
          || aiot_decode_frame(r2d_chips, header.size, sizeof(command), false, false, true, &command) != AIOT_RESULT_OK
          || command != AIOT_INVENTORY_COMMAND) {
        fprintf(stderr, "AIOT_T2_R2D_REJECT reason=decode tag_id=%u\n", tag_id);
        continue;
      }
      r2d_received = true;
      r2d_timestamp = header.timestamp;
      printf("AIOT_T2_R2D_ACCEPT tag_id=%u\n", tag_id);
    }

    if (cw_samples == 0 || !r2d_received)
      continue;

    c16_t *reflected = calloc(chips_len, sizeof(*reflected));
    if (reflected == NULL) {
      free(samples);
      return 1;
    }
    for (size_t i = 0; i < chips_len; ++i) {
      reflected[i].r = cw[i].r * chips[i];
      reflected[i].i = cw[i].i * chips[i];
    }
    const samplesBlockHeader_t d2r = {
        .size = chips_len,
        .nbAnt = 1,
        .timestamp = cw_timestamp > r2d_timestamp ? cw_timestamp : r2d_timestamp,
        .option_value = tag_id,
        .option_flag = OPTION_AIOT_T2_D2R,
        .beam_map = 1,
    };
    aiot_write_rfsim_packet(socket, &d2r, reflected);
    printf("AIOT_T2_BACKSCATTER tag_id=%u cw_samples=%zu d2r_samples=%zu\n", tag_id, cw_samples, chips_len);
    free(reflected);
    free(samples);
    close(socket);
    return 0;
  }

  free(samples);
  fprintf(stderr, "AIOT_T2_CW_REJECT reason=connection_closed\n");
  return 1;
}

static int aiot_reader_rfsim_cli(int argc, char **argv)
{
  if (argc != 6) {
    fprintf(stderr, "Usage: %s --aiot-reader-rfsim <server> <port> <tag-id> <reader:awake|reader:asleep>\n", argv[0]);
    return 2;
  }

  uint32_t port = 0;
  uint32_t tag_id = 0;
  if (!aiot_parse_u32(argv[3], 1, UINT16_MAX, &port) || !aiot_parse_u32(argv[4], 1, 60, &tag_id)
      || (strcmp(argv[5], "reader:awake") != 0 && strcmp(argv[5], "reader:asleep") != 0)) {
    fprintf(stderr, "AIOT_T2_ARGUMENT_REJECT\n");
    return 2;
  }

  const int socket = client_start(argv[2], port);
  setblocking(socket, blocking);
  samplesBlockHeader_t header;
  c16_t *samples = NULL;
  size_t capacity = 0;
  if (!aiot_read_rfsim_packet(socket, &header, &samples, &capacity)) {
    free(samples);
    fprintf(stderr, "AIOT_T2_RFSIM_SYNC_REJECT\n");
    return 1;
  }

  if (strcmp(argv[5], "reader:asleep") == 0) {
    printf("AIOT_T2_R2D_REJECT reason=reader_asleep tag_id=%u\n", tag_id);
    free(samples);
    close(socket);
    return 0;
  }

  const uint8_t command = AIOT_INVENTORY_COMMAND;
  uint8_t r2d_chips[AIOT_T2_MAX_RF_SAMPLES];
  size_t r2d_chips_len = 0;
  if (aiot_encode_frame(&command, sizeof(command), false, r2d_chips, sizeof(r2d_chips), &r2d_chips_len)
      != AIOT_RESULT_OK) {
    free(samples);
    close(socket);
    return 1;
  }
  c16_t r2d[AIOT_T2_MAX_RF_SAMPLES] = {0};
  for (size_t i = 0; i < r2d_chips_len; ++i)
    r2d[i].r = r2d_chips[i];
  const samplesBlockHeader_t r2d_header = {
      .size = r2d_chips_len,
      .nbAnt = 1,
      .timestamp = header.timestamp + header.size,
      .option_value = tag_id,
      .option_flag = OPTION_AIOT_T2_R2D,
      .beam_map = 1,
  };
  aiot_write_rfsim_packet(socket, &r2d_header, r2d);
  printf("AIOT_T2_R2D_SENT tag_id=%u samples=%zu\n", tag_id, r2d_chips_len);

  while (aiot_read_rfsim_packet(socket, &header, &samples, &capacity)) {
    if ((header.option_flag & OPTION_AIOT_T2_D2R) == 0 || header.option_value != tag_id)
      continue;
    uint8_t chips[AIOT_T2_MAX_RF_SAMPLES];
    size_t inventory_len = 0;
    uint8_t inventory[AIOT_MAX_PAYLOAD_BYTES];
    if (header.nbAnt != 1 || !aiot_samples_to_chips(samples, header.size, chips)
        || !aiot_d2r_payload_length(header.size, &inventory_len)
        || aiot_decode_frame(chips, header.size, inventory_len, true, true, true, inventory) != AIOT_RESULT_OK) {
      fprintf(stderr, "AIOT_T2_D2R_REJECT reason=decode tag_id=%u\n", tag_id);
      free(samples);
      close(socket);
      return 1;
    }
    printf("AIOT_T2_D2R_CRC_OK tag_id=%u payload=", tag_id);
    for (size_t i = 0; i < inventory_len; ++i)
      printf("%02x", inventory[i]);
    printf("\nAIOT_T2_UE_REPORT_READY tag_id=%u transport=pending\n", tag_id);
    free(samples);
    close(socket);
    return 0;
  }

  free(samples);
  fprintf(stderr, "AIOT_T2_TIMEOUT tag_id=%u\n", tag_id);
  return 1;
}

int main(int argc, char *argv[]) {
  if (argc >= 2 && strcmp(argv[1], "--aiot-tag-self-test") == 0)
    return aiot_tag_self_test();
  if (argc >= 2 && strcmp(argv[1], "--aiot-tag") == 0) {
    crcTableInit();
    return aiot_tag_cli(argc, argv);
  }
  if (argc >= 2 && strcmp(argv[1], "--aiot-cw-rfsim") == 0)
    return aiot_cw_rfsim_cli(argc, argv);
  if (argc >= 2 && strcmp(argv[1], "--aiot-tag-rfsim") == 0) {
    crcTableInit();
    return aiot_tag_rfsim_cli(argc, argv);
  }
  if (argc >= 2 && strcmp(argv[1], "--aiot-reader-rfsim") == 0) {
    crcTableInit();
    return aiot_reader_rfsim_cli(argc, argv);
  }

  if(argc < 4) {
    printf("Need parameters: source file, server or destination IP, TCP port (4043), "
           "'UL|DL' if raw 2*16bits format: UL for UL IQ, DL for DL IQs\n"
           "Or: --aiot-tag-self-test\n"
           "Or: --aiot-tag <cw:on|off> <reader:awake|asleep> <none|invalid00|invalid11|crc|timeout> <inventory-hex>\n"
           "Or: --aiot-cw-rfsim <server> <port> <samples> <amplitude>\n"
           "Or: --aiot-tag-rfsim <server> <port> <tag-id> <inventory-hex>\n"
           "Or: --aiot-reader-rfsim <server> <port> <tag-id> <reader:awake|reader:asleep>\n");
    exit(1);
  }

  int fd;
  AssertFatal((fd=open(argv[1],O_RDONLY)) != -1, "file: %s", argv[1]);
  off_t fileSize=lseek(fd, 0, SEEK_END);
  int serviceSock;

  if (strcmp(argv[2],"server")==0) {
    serviceSock=server_start(atoi(argv[3]));
  } else {
    serviceSock=client_start(argv[2],atoi(argv[3]));
  }

  bool raw = false;

  if ( argc == 5 ) {
    raw=true;
  }

  samplesBlockHeader_t header;
  int bufSize=100000;
  void *buff=malloc(bufSize);
  uint64_t timestamp=0;
  const int blockSize=1920;
  // If fileSize is not multiple of blockSize*4 then discard remaining samples
  fileSize = (fileSize/(blockSize<<2))*(blockSize<<2);

  while (1) {
    //Rewind the file to loop on the samples
    if ( lseek(fd, 0, SEEK_CUR) >= fileSize )
      lseek(fd, 0, SEEK_SET);

    // Read one block and send it
    setblocking(serviceSock, blocking);

    if ( raw ) {
      header.size=blockSize;
      header.nbAnt=1;
      header.timestamp=timestamp;
      timestamp+=blockSize;
      header.option_value=0;
      header.option_flag=0;
    } else {
      AssertFatal(read(fd,&header,sizeof(header)), "");
    }

    fullwrite(serviceSock, &header, sizeof(header));
    int dataSize=sizeof(int32_t)*header.size*header.nbAnt;

    if (dataSize>bufSize) {
      void *new_buff = realloc(buff, dataSize);

      if (new_buff == NULL) {
        free(buff);
        AssertFatal(1, "Could not reallocate");
      } else {
        buff = new_buff;
      }
    }

    AssertFatal(read(fd,buff,dataSize) == dataSize, "");

    if (raw) // UHD shifts the 12 ADC values in MSB
      for (int i=0; i<header.size*header.nbAnt*2; i++)
        ((int16_t *)buff)[i]/=16;

    usleep(1000);
    printf("sending at ts: %lu, number of samples: %d\n",
           header.timestamp, header.size);
    fullwrite(serviceSock, buff, dataSize);
    // Purge incoming samples
    setblocking(serviceSock, notBlocking);
    int ret;

    do {
      char buff[64000];
      ret=read(serviceSock, buff, 64000);

      if ( ret<0 && !( errno == EAGAIN || errno == EWOULDBLOCK ) ) {
        printf("error: %s\n", strerror(errno));
        exit(1);
      }
    } while ( ret > 0 ) ;
  }

  return 0;
}
