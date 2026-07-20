#ifndef AIOTF_INVENTORY_H
#define AIOTF_INVENTORY_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#define AIOTF_MAX_TAGS 60U
#define AIOTF_MAX_READERS_PER_TAG 2U
#define AIOTF_MAX_PAYLOAD_BYTES 16U
#define AIOTF_MAX_REPORT_EVIDENCE 8U
#define AIOTF_READER_UE1 1U
#define AIOTF_READER_UE2 2U

typedef enum {
  AIOTF_RESULT_REJECTED = 0,
  AIOTF_RESULT_PENDING,
  AIOTF_RESULT_COMPLETED,
  AIOTF_RESULT_TIMEOUT,
} aiotf_inventory_result_t;

typedef enum {
  AIOTF_REQUEST_ACCEPTED = 0,
  AIOTF_REQUEST_INVALID_ARGUMENT,
  AIOTF_REQUEST_INVALID_TAG,
  AIOTF_REQUEST_INVALID_TIMEOUT,
  AIOTF_REQUEST_DEADLINE_OVERFLOW,
  AIOTF_REQUEST_CORRELATION_EXHAUSTED,
} aiotf_request_status_t;

typedef enum {
  AIOTF_REPORT_ACCEPTED = 0,
  AIOTF_REPORT_INVALID_ARGUMENT,
  AIOTF_REPORT_NOT_PENDING,
  AIOTF_REPORT_AFTER_TIMEOUT,
  AIOTF_REPORT_TAG_MISMATCH,
  AIOTF_REPORT_INVALID_READER,
  AIOTF_REPORT_INVALID_PAYLOAD_LENGTH,
  AIOTF_REPORT_CRC_FAILURE,
} aiotf_report_status_t;

typedef struct {
  uint32_t tag_id;
  uint32_t timeout_ms;
} aiotf_inventory_request_t;

typedef struct {
  uint64_t correlation_id;
  uint64_t session_id;
  uint32_t tag_id;
  uint32_t binding_epoch;
  uint32_t reader_handle;
  bool crc_valid;
  size_t payload_len;
  uint8_t payload[AIOTF_MAX_PAYLOAD_BYTES];
} aiotf_inventory_report_t;

typedef struct {
  uint64_t next_correlation_id;
  uint64_t next_session_id;
} aiotf_inventory_context_t;

typedef enum {
  AIOTF_RESOURCE_SERIALIZED_SINGLE_TAG = 1,
} aiotf_resource_policy_t;

typedef struct {
  uint32_t tag_id;
  uint32_t eligible_readers[AIOTF_MAX_READERS_PER_TAG];
  size_t eligible_reader_count;
  uint32_t default_primary_reader;
  uint32_t primary_reader;
  uint32_t binding_epoch;
  aiotf_resource_policy_t resource_policy;
} aiotf_reader_binding_t;

typedef struct {
  aiotf_reader_binding_t bindings[AIOTF_MAX_TAGS];
} aiotf_binding_table_t;

typedef enum {
  AIOTF_READER_MODE_NORMAL = 0,
  AIOTF_READER_MODE_DIVERSITY,
} aiotf_reader_mode_t;

typedef enum {
  AIOTF_READER_ROLE_R2D_PRIMARY = 0,
  AIOTF_READER_ROLE_D2R_OBSERVER,
} aiotf_reader_role_t;

typedef enum {
  AIOTF_READER_SELECTION_OK = 0,
  AIOTF_READER_SELECTION_INVALID_ARGUMENT,
  AIOTF_READER_SELECTION_INVALID_BINDING,
  AIOTF_READER_SELECTION_PRIMARY_UNAVAILABLE,
  AIOTF_READER_SELECTION_DIVERSITY_NOT_ELIGIBLE,
} aiotf_reader_selection_status_t;

typedef struct {
  uint32_t tag_id;
  uint32_t binding_epoch;
  uint32_t primary_reader;
  uint32_t active_readers[AIOTF_MAX_READERS_PER_TAG];
  aiotf_reader_role_t active_roles[AIOTF_MAX_READERS_PER_TAG];
  size_t active_reader_count;
} aiotf_reader_selection_t;

typedef enum {
  AIOTF_FAILOVER_OK = 0,
  AIOTF_FAILOVER_INVALID_ARGUMENT,
  AIOTF_FAILOVER_INVALID_BINDING,
  AIOTF_FAILOVER_AFTER_R2D,
  AIOTF_FAILOVER_NOT_NEEDED,
  AIOTF_FAILOVER_EXCLUSIVE_BINDING,
  AIOTF_FAILOVER_ALTERNATIVE_UNAVAILABLE,
  AIOTF_FAILOVER_EPOCH_EXHAUSTED,
} aiotf_failover_status_t;

typedef enum {
  AIOTF_SCHEDULE_OK = 0,
  AIOTF_SCHEDULE_INVALID_ARGUMENT,
  AIOTF_SCHEDULE_INVALID_TAG_COUNT,
  AIOTF_SCHEDULE_INVALID_TAG,
  AIOTF_SCHEDULE_DUPLICATE_TAG,
  AIOTF_SCHEDULE_OUTPUT_TOO_SMALL,
  AIOTF_SCHEDULE_SLOT_OVERFLOW,
  AIOTF_SCHEDULE_SESSION_EXHAUSTED,
} aiotf_schedule_status_t;

typedef struct {
  uint64_t correlation_id;
  uint64_t session_id;
  uint64_t response_slot;
  uint32_t tag_id;
  uint32_t binding_epoch;
  aiotf_inventory_result_t result;
} aiotf_tag_transaction_t;

typedef enum {
  AIOTF_EVIDENCE_INVALID_CORRELATION = 0,
  AIOTF_EVIDENCE_INVALID_SESSION,
  AIOTF_EVIDENCE_INVALID_TAG,
  AIOTF_EVIDENCE_STALE_EPOCH,
  AIOTF_EVIDENCE_INACTIVE_READER,
  AIOTF_EVIDENCE_AFTER_DEADLINE,
  AIOTF_EVIDENCE_CRC_FAILURE,
  AIOTF_EVIDENCE_INVALID_PAYLOAD_LENGTH,
  AIOTF_EVIDENCE_DUPLICATE,
  AIOTF_EVIDENCE_CONFLICT,
} aiotf_report_evidence_kind_t;

typedef struct {
  aiotf_report_evidence_kind_t kind;
  aiotf_inventory_report_t report;
} aiotf_report_evidence_t;

typedef struct {
  aiotf_tag_transaction_t transaction;
  aiotf_reader_selection_t readers;
  uint64_t deadline_ms;
  bool has_result;
  bool conflicting_valid_reports;
  aiotf_inventory_report_t result_report;
  aiotf_report_evidence_t evidence[AIOTF_MAX_REPORT_EVIDENCE];
  size_t evidence_count;
  size_t evidence_dropped;
  size_t invalid_report_count;
  size_t duplicate_report_count;
  size_t conflict_report_count;
  size_t stale_epoch_report_count;
} aiotf_report_arbitration_t;

typedef enum {
  AIOTF_ARBITRATION_FIRST_VALID = 0,
  AIOTF_ARBITRATION_DUPLICATE,
  AIOTF_ARBITRATION_CONFLICT,
  AIOTF_ARBITRATION_INVALID_ARGUMENT,
  AIOTF_ARBITRATION_INVALID_CORRELATION,
  AIOTF_ARBITRATION_INVALID_SESSION,
  AIOTF_ARBITRATION_INVALID_TAG,
  AIOTF_ARBITRATION_STALE_EPOCH,
  AIOTF_ARBITRATION_INACTIVE_READER,
  AIOTF_ARBITRATION_AFTER_DEADLINE,
  AIOTF_ARBITRATION_CRC_FAILURE,
  AIOTF_ARBITRATION_INVALID_PAYLOAD_LENGTH,
} aiotf_arbitration_status_t;

typedef struct {
  uint32_t reader_handle;
  uint32_t tag_id;
  uint32_t frame;
  uint32_t slot;
  bool crc_valid;
  size_t payload_len;
  uint8_t payload[AIOTF_MAX_PAYLOAD_BYTES];
} aiotf_diagnostic_report_t;

typedef struct {
  uint32_t frame;
  uint32_t slot;
  aiotf_report_arbitration_t arbitration;
} aiotf_pending_report_context_t;

typedef enum {
  AIOTF_DIAGNOSTIC_ASSOCIATED = 0,
  AIOTF_DIAGNOSTIC_INVALID_ARGUMENT,
  AIOTF_DIAGNOSTIC_NO_PENDING_CONTEXT,
  AIOTF_DIAGNOSTIC_AMBIGUOUS_CONTEXT,
  AIOTF_DIAGNOSTIC_ARBITRATION_REJECTED,
} aiotf_diagnostic_status_t;

typedef struct {
  uint64_t correlation_id;
  uint64_t accepted_at_ms;
  uint64_t deadline_ms;
  uint32_t tag_id;
  aiotf_inventory_result_t result;
  aiotf_request_status_t rejection_reason;
  bool has_report;
  aiotf_inventory_report_t report;
} aiotf_inventory_session_t;

/* The caller serializes access to a context and its sessions. */
void aiotf_inventory_context_init(aiotf_inventory_context_t *context);

bool aiotf_binding_table_init(aiotf_binding_table_t *table);

const aiotf_reader_binding_t *aiotf_binding_table_get(const aiotf_binding_table_t *table, uint32_t tag_id);

bool aiotf_binding_table_validate_profile(const aiotf_binding_table_t *table);

aiotf_reader_selection_status_t aiotf_select_readers(const aiotf_reader_binding_t *binding,
                                                     aiotf_reader_mode_t mode,
                                                     bool ue1_available,
                                                     bool ue2_available,
                                                     aiotf_reader_selection_t *selection);

aiotf_failover_status_t aiotf_failover_primary(aiotf_reader_binding_t *binding,
                                               bool r2d_transmitted,
                                               bool ue1_available,
                                               bool ue2_available);

aiotf_schedule_status_t aiotf_schedule_transactions(aiotf_inventory_context_t *context,
                                                    const aiotf_binding_table_t *table,
                                                    uint64_t correlation_id,
                                                    const uint32_t *tag_ids,
                                                    size_t tag_count,
                                                    uint64_t first_response_slot,
                                                    aiotf_tag_transaction_t *transactions,
                                                    size_t transaction_capacity,
                                                    size_t *transaction_count);

bool aiotf_report_arbitration_init(aiotf_report_arbitration_t *arbitration,
                                   const aiotf_tag_transaction_t *transaction,
                                   const aiotf_reader_selection_t *readers,
                                   uint64_t deadline_ms);

bool aiotf_report_arbitration_expire(aiotf_report_arbitration_t *arbitration, uint64_t now_ms);

aiotf_arbitration_status_t aiotf_arbitrate_report(aiotf_report_arbitration_t *arbitration,
                                                  const aiotf_inventory_report_t *report,
                                                  uint64_t now_ms);

aiotf_diagnostic_status_t aiotf_diagnostic_associate_report(aiotf_pending_report_context_t *contexts,
                                                            size_t context_count,
                                                            const aiotf_diagnostic_report_t *report,
                                                            uint64_t now_ms,
                                                            size_t *matched_context,
                                                            aiotf_arbitration_status_t *arbitration_status);

aiotf_request_status_t aiotf_inventory_start(aiotf_inventory_context_t *context,
                                             const aiotf_inventory_request_t *request,
                                             uint64_t now_ms,
                                             aiotf_inventory_session_t *session);

bool aiotf_inventory_expire(aiotf_inventory_session_t *session, uint64_t now_ms);

aiotf_report_status_t aiotf_inventory_associate_report(aiotf_inventory_session_t *session,
                                                       const aiotf_inventory_report_t *report,
                                                       uint64_t now_ms);

#endif
