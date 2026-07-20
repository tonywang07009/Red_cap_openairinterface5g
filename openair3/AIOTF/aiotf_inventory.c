#include "aiotf_inventory.h"

#include <limits.h>
#include <string.h>

void aiotf_inventory_context_init(aiotf_inventory_context_t *context)
{
  if (context != NULL) {
    context->next_correlation_id = 1;
    context->next_session_id = 1;
  }
}

static bool reader_is_eligible(const aiotf_reader_binding_t *binding, uint32_t reader_handle)
{
  for (size_t i = 0; i < binding->eligible_reader_count; ++i) {
    if (binding->eligible_readers[i] == reader_handle)
      return true;
  }
  return false;
}

bool aiotf_binding_table_init(aiotf_binding_table_t *table)
{
  if (table == NULL)
    return false;

  memset(table, 0, sizeof(*table));
  for (uint32_t tag_id = 1; tag_id <= AIOTF_MAX_TAGS; ++tag_id) {
    aiotf_reader_binding_t *binding = &table->bindings[tag_id - 1];
    *binding = (aiotf_reader_binding_t){
        .tag_id = tag_id,
        .default_primary_reader = tag_id <= 30 ? AIOTF_READER_UE1 : AIOTF_READER_UE2,
        .primary_reader = tag_id <= 30 ? AIOTF_READER_UE1 : AIOTF_READER_UE2,
        .binding_epoch = 1,
        .resource_policy = AIOTF_RESOURCE_SERIALIZED_SINGLE_TAG,
    };
    if (tag_id <= 20) {
      binding->eligible_readers[0] = AIOTF_READER_UE1;
      binding->eligible_reader_count = 1;
    } else if (tag_id <= 40) {
      binding->eligible_readers[0] = AIOTF_READER_UE1;
      binding->eligible_readers[1] = AIOTF_READER_UE2;
      binding->eligible_reader_count = 2;
    } else {
      binding->eligible_readers[0] = AIOTF_READER_UE2;
      binding->eligible_reader_count = 1;
    }
  }
  return true;
}

const aiotf_reader_binding_t *aiotf_binding_table_get(const aiotf_binding_table_t *table, uint32_t tag_id)
{
  if (table == NULL || tag_id == 0 || tag_id > AIOTF_MAX_TAGS)
    return NULL;
  return &table->bindings[tag_id - 1];
}

bool aiotf_binding_table_validate_profile(const aiotf_binding_table_t *table)
{
  if (table == NULL)
    return false;

  for (uint32_t tag_id = 1; tag_id <= AIOTF_MAX_TAGS; ++tag_id) {
    const aiotf_reader_binding_t *binding = aiotf_binding_table_get(table, tag_id);
    const size_t expected_count = tag_id <= 20 || tag_id > 40 ? 1 : 2;
    const uint32_t expected_first = tag_id <= 40 ? AIOTF_READER_UE1 : AIOTF_READER_UE2;
    const uint32_t expected_primary = tag_id <= 30 ? AIOTF_READER_UE1 : AIOTF_READER_UE2;
    if (binding == NULL || binding->tag_id != tag_id || binding->eligible_reader_count != expected_count
        || binding->eligible_readers[0] != expected_first || binding->default_primary_reader != expected_primary
        || binding->primary_reader != expected_primary || !reader_is_eligible(binding, binding->primary_reader)
        || binding->binding_epoch == 0
        || binding->resource_policy != AIOTF_RESOURCE_SERIALIZED_SINGLE_TAG)
      return false;
    if ((expected_count == 1 && binding->eligible_readers[1] != 0)
        || (expected_count == 2 && binding->eligible_readers[1] != AIOTF_READER_UE2))
      return false;
  }
  return true;
}

static bool reader_is_available(uint32_t reader_handle, bool ue1_available, bool ue2_available)
{
  return reader_handle == AIOTF_READER_UE1 ? ue1_available
         : reader_handle == AIOTF_READER_UE2 ? ue2_available
                                            : false;
}

aiotf_reader_selection_status_t aiotf_select_readers(const aiotf_reader_binding_t *binding,
                                                     aiotf_reader_mode_t mode,
                                                     bool ue1_available,
                                                     bool ue2_available,
                                                     aiotf_reader_selection_t *selection)
{
  if (binding == NULL || selection == NULL)
    return AIOTF_READER_SELECTION_INVALID_ARGUMENT;
  memset(selection, 0, sizeof(*selection));
  if (binding->tag_id == 0 || binding->tag_id > AIOTF_MAX_TAGS || binding->eligible_reader_count == 0
      || binding->eligible_reader_count > AIOTF_MAX_READERS_PER_TAG || binding->binding_epoch == 0
      || !reader_is_eligible(binding, binding->primary_reader))
    return AIOTF_READER_SELECTION_INVALID_BINDING;
  if (mode != AIOTF_READER_MODE_NORMAL && mode != AIOTF_READER_MODE_DIVERSITY)
    return AIOTF_READER_SELECTION_INVALID_ARGUMENT;
  if (!reader_is_available(binding->primary_reader, ue1_available, ue2_available))
    return AIOTF_READER_SELECTION_PRIMARY_UNAVAILABLE;
  if (mode == AIOTF_READER_MODE_DIVERSITY && binding->eligible_reader_count != AIOTF_MAX_READERS_PER_TAG)
    return AIOTF_READER_SELECTION_DIVERSITY_NOT_ELIGIBLE;

  *selection = (aiotf_reader_selection_t){
      .tag_id = binding->tag_id,
      .binding_epoch = binding->binding_epoch,
      .primary_reader = binding->primary_reader,
      .active_readers = {binding->primary_reader},
      .active_roles = {AIOTF_READER_ROLE_R2D_PRIMARY},
      .active_reader_count = 1,
  };
  if (mode == AIOTF_READER_MODE_NORMAL)
    return AIOTF_READER_SELECTION_OK;

  for (size_t i = 0; i < binding->eligible_reader_count; ++i) {
    const uint32_t reader = binding->eligible_readers[i];
    if (reader != binding->primary_reader && reader_is_available(reader, ue1_available, ue2_available)) {
      selection->active_readers[1] = reader;
      selection->active_roles[1] = AIOTF_READER_ROLE_D2R_OBSERVER;
      selection->active_reader_count = 2;
      break;
    }
  }
  return AIOTF_READER_SELECTION_OK;
}

aiotf_failover_status_t aiotf_failover_primary(aiotf_reader_binding_t *binding,
                                               bool r2d_transmitted,
                                               bool ue1_available,
                                               bool ue2_available)
{
  if (binding == NULL)
    return AIOTF_FAILOVER_INVALID_ARGUMENT;
  if (binding->eligible_reader_count == 0 || binding->eligible_reader_count > AIOTF_MAX_READERS_PER_TAG
      || !reader_is_eligible(binding, binding->primary_reader) || binding->binding_epoch == 0)
    return AIOTF_FAILOVER_INVALID_BINDING;
  if (r2d_transmitted)
    return AIOTF_FAILOVER_AFTER_R2D;
  if (reader_is_available(binding->primary_reader, ue1_available, ue2_available))
    return AIOTF_FAILOVER_NOT_NEEDED;
  if (binding->eligible_reader_count != AIOTF_MAX_READERS_PER_TAG)
    return AIOTF_FAILOVER_EXCLUSIVE_BINDING;

  uint32_t alternative = 0;
  for (size_t i = 0; i < binding->eligible_reader_count; ++i) {
    const uint32_t reader = binding->eligible_readers[i];
    if (reader != binding->primary_reader && reader_is_available(reader, ue1_available, ue2_available)) {
      alternative = reader;
      break;
    }
  }
  if (alternative == 0)
    return AIOTF_FAILOVER_ALTERNATIVE_UNAVAILABLE;
  if (binding->binding_epoch == UINT32_MAX)
    return AIOTF_FAILOVER_EPOCH_EXHAUSTED;

  binding->primary_reader = alternative;
  ++binding->binding_epoch;
  return AIOTF_FAILOVER_OK;
}

aiotf_schedule_status_t aiotf_schedule_transactions(aiotf_inventory_context_t *context,
                                                    const aiotf_binding_table_t *table,
                                                    uint64_t correlation_id,
                                                    const uint32_t *tag_ids,
                                                    size_t tag_count,
                                                    uint64_t first_response_slot,
                                                    aiotf_tag_transaction_t *transactions,
                                                    size_t transaction_capacity,
                                                    size_t *transaction_count)
{
  if (transaction_count != NULL)
    *transaction_count = 0;
  if (context == NULL || table == NULL || correlation_id == 0 || tag_ids == NULL || transactions == NULL
      || transaction_count == NULL)
    return AIOTF_SCHEDULE_INVALID_ARGUMENT;
  if (tag_count == 0 || tag_count > AIOTF_MAX_TAGS)
    return AIOTF_SCHEDULE_INVALID_TAG_COUNT;
  if (transaction_capacity < tag_count)
    return AIOTF_SCHEDULE_OUTPUT_TOO_SMALL;
  if (first_response_slot > UINT64_MAX - (tag_count - 1))
    return AIOTF_SCHEDULE_SLOT_OVERFLOW;
  if (context->next_session_id == 0 || context->next_session_id > UINT64_MAX - (tag_count - 1))
    return AIOTF_SCHEDULE_SESSION_EXHAUSTED;

  bool selected[AIOTF_MAX_TAGS + 1] = {false};
  for (size_t i = 0; i < tag_count; ++i) {
    const uint32_t tag_id = tag_ids[i];
    if (aiotf_binding_table_get(table, tag_id) == NULL)
      return AIOTF_SCHEDULE_INVALID_TAG;
    if (selected[tag_id])
      return AIOTF_SCHEDULE_DUPLICATE_TAG;
    selected[tag_id] = true;
  }

  size_t output_index = 0;
  for (uint32_t tag_id = 1; tag_id <= AIOTF_MAX_TAGS; ++tag_id) {
    if (!selected[tag_id])
      continue;
    const aiotf_reader_binding_t *binding = aiotf_binding_table_get(table, tag_id);
    transactions[output_index] = (aiotf_tag_transaction_t){
        .correlation_id = correlation_id,
        .session_id = context->next_session_id + output_index,
        .response_slot = first_response_slot + output_index,
        .tag_id = tag_id,
        .binding_epoch = binding->binding_epoch,
        .result = AIOTF_RESULT_PENDING,
    };
    ++output_index;
  }
  context->next_session_id += tag_count;
  *transaction_count = output_index;
  return AIOTF_SCHEDULE_OK;
}

static bool selection_is_valid_for_transaction(const aiotf_reader_selection_t *readers,
                                               const aiotf_tag_transaction_t *transaction)
{
  if (readers->tag_id != transaction->tag_id || readers->binding_epoch != transaction->binding_epoch
      || readers->active_reader_count == 0 || readers->active_reader_count > AIOTF_MAX_READERS_PER_TAG
      || readers->primary_reader != readers->active_readers[0]
      || readers->active_roles[0] != AIOTF_READER_ROLE_R2D_PRIMARY)
    return false;
  for (size_t i = 0; i < readers->active_reader_count; ++i) {
    const uint32_t reader = readers->active_readers[i];
    if (reader != AIOTF_READER_UE1 && reader != AIOTF_READER_UE2)
      return false;
    if (i > 0 && (reader == readers->active_readers[0] || readers->active_roles[i] != AIOTF_READER_ROLE_D2R_OBSERVER))
      return false;
  }
  return true;
}

bool aiotf_report_arbitration_init(aiotf_report_arbitration_t *arbitration,
                                   const aiotf_tag_transaction_t *transaction,
                                   const aiotf_reader_selection_t *readers,
                                   uint64_t deadline_ms)
{
  if (arbitration == NULL || transaction == NULL || readers == NULL || transaction->correlation_id == 0
      || transaction->session_id == 0 || transaction->result != AIOTF_RESULT_PENDING || deadline_ms == 0
      || !selection_is_valid_for_transaction(readers, transaction))
    return false;
  *arbitration = (aiotf_report_arbitration_t){
      .transaction = *transaction,
      .readers = *readers,
      .deadline_ms = deadline_ms,
  };
  return true;
}

bool aiotf_report_arbitration_expire(aiotf_report_arbitration_t *arbitration, uint64_t now_ms)
{
  if (arbitration == NULL || arbitration->has_result || arbitration->transaction.result != AIOTF_RESULT_PENDING
      || now_ms < arbitration->deadline_ms)
    return false;
  arbitration->transaction.result = AIOTF_RESULT_TIMEOUT;
  return true;
}

static bool selection_contains_reader(const aiotf_reader_selection_t *readers, uint32_t reader_handle)
{
  for (size_t i = 0; i < readers->active_reader_count; ++i) {
    if (readers->active_readers[i] == reader_handle)
      return true;
  }
  return false;
}

static void record_evidence(aiotf_report_arbitration_t *arbitration,
                            aiotf_report_evidence_kind_t kind,
                            const aiotf_inventory_report_t *report)
{
  if (arbitration->evidence_count < AIOTF_MAX_REPORT_EVIDENCE) {
    arbitration->evidence[arbitration->evidence_count++] = (aiotf_report_evidence_t){
        .kind = kind,
        .report = *report,
    };
  } else {
    ++arbitration->evidence_dropped;
  }
}

static aiotf_arbitration_status_t reject_report(aiotf_report_arbitration_t *arbitration,
                                                aiotf_report_evidence_kind_t kind,
                                                aiotf_arbitration_status_t status,
                                                const aiotf_inventory_report_t *report)
{
  record_evidence(arbitration, kind, report);
  ++arbitration->invalid_report_count;
  if (kind == AIOTF_EVIDENCE_STALE_EPOCH)
    ++arbitration->stale_epoch_report_count;
  return status;
}

aiotf_arbitration_status_t aiotf_arbitrate_report(aiotf_report_arbitration_t *arbitration,
                                                  const aiotf_inventory_report_t *report,
                                                  uint64_t now_ms)
{
  if (arbitration == NULL || report == NULL)
    return AIOTF_ARBITRATION_INVALID_ARGUMENT;
  if (report->correlation_id != arbitration->transaction.correlation_id)
    return reject_report(arbitration,
                         AIOTF_EVIDENCE_INVALID_CORRELATION,
                         AIOTF_ARBITRATION_INVALID_CORRELATION,
                         report);
  if (report->session_id != arbitration->transaction.session_id)
    return reject_report(arbitration, AIOTF_EVIDENCE_INVALID_SESSION, AIOTF_ARBITRATION_INVALID_SESSION, report);
  if (report->tag_id != arbitration->transaction.tag_id)
    return reject_report(arbitration, AIOTF_EVIDENCE_INVALID_TAG, AIOTF_ARBITRATION_INVALID_TAG, report);
  if (report->binding_epoch != arbitration->transaction.binding_epoch)
    return reject_report(arbitration, AIOTF_EVIDENCE_STALE_EPOCH, AIOTF_ARBITRATION_STALE_EPOCH, report);
  if (!selection_contains_reader(&arbitration->readers, report->reader_handle))
    return reject_report(arbitration, AIOTF_EVIDENCE_INACTIVE_READER, AIOTF_ARBITRATION_INACTIVE_READER, report);
  if (now_ms >= arbitration->deadline_ms) {
    aiotf_report_arbitration_expire(arbitration, now_ms);
    return reject_report(arbitration, AIOTF_EVIDENCE_AFTER_DEADLINE, AIOTF_ARBITRATION_AFTER_DEADLINE, report);
  }
  if (!report->crc_valid)
    return reject_report(arbitration, AIOTF_EVIDENCE_CRC_FAILURE, AIOTF_ARBITRATION_CRC_FAILURE, report);
  if (report->payload_len == 0 || report->payload_len > AIOTF_MAX_PAYLOAD_BYTES)
    return reject_report(
        arbitration, AIOTF_EVIDENCE_INVALID_PAYLOAD_LENGTH, AIOTF_ARBITRATION_INVALID_PAYLOAD_LENGTH, report);

  if (!arbitration->has_result) {
    arbitration->result_report = *report;
    arbitration->has_result = true;
    arbitration->transaction.result = AIOTF_RESULT_COMPLETED;
    return AIOTF_ARBITRATION_FIRST_VALID;
  }

  if (report->payload_len == arbitration->result_report.payload_len
      && memcmp(report->payload, arbitration->result_report.payload, report->payload_len) == 0) {
    record_evidence(arbitration, AIOTF_EVIDENCE_DUPLICATE, report);
    ++arbitration->duplicate_report_count;
    return AIOTF_ARBITRATION_DUPLICATE;
  }

  record_evidence(arbitration, AIOTF_EVIDENCE_CONFLICT, report);
  arbitration->conflicting_valid_reports = true;
  ++arbitration->conflict_report_count;
  return AIOTF_ARBITRATION_CONFLICT;
}

aiotf_diagnostic_status_t aiotf_diagnostic_associate_report(aiotf_pending_report_context_t *contexts,
                                                            size_t context_count,
                                                            const aiotf_diagnostic_report_t *report,
                                                            uint64_t now_ms,
                                                            size_t *matched_context,
                                                            aiotf_arbitration_status_t *arbitration_status)
{
  if (matched_context != NULL)
    *matched_context = SIZE_MAX;
  if (arbitration_status != NULL)
    *arbitration_status = AIOTF_ARBITRATION_INVALID_ARGUMENT;
  if (contexts == NULL || report == NULL || matched_context == NULL || arbitration_status == NULL)
    return AIOTF_DIAGNOSTIC_INVALID_ARGUMENT;
  if (context_count == 0)
    return AIOTF_DIAGNOSTIC_NO_PENDING_CONTEXT;

  size_t candidate = SIZE_MAX;
  size_t candidate_count = 0;
  for (size_t i = 0; i < context_count; ++i) {
    const aiotf_pending_report_context_t *context = &contexts[i];
    if (context->arbitration.transaction.tag_id == report->tag_id && context->frame == report->frame
        && context->slot == report->slot) {
      candidate = i;
      ++candidate_count;
    }
  }
  if (candidate_count == 0)
    return AIOTF_DIAGNOSTIC_NO_PENDING_CONTEXT;
  if (candidate_count != 1)
    return AIOTF_DIAGNOSTIC_AMBIGUOUS_CONTEXT;

  aiotf_report_arbitration_t *arbitration = &contexts[candidate].arbitration;
  const aiotf_inventory_report_t inventory_report = {
      .correlation_id = arbitration->transaction.correlation_id,
      .session_id = arbitration->transaction.session_id,
      .tag_id = report->tag_id,
      .binding_epoch = arbitration->transaction.binding_epoch,
      .reader_handle = report->reader_handle,
      .crc_valid = report->crc_valid,
      .payload_len = report->payload_len,
  };
  aiotf_inventory_report_t associated_report = inventory_report;
  if (report->payload_len <= AIOTF_MAX_PAYLOAD_BYTES)
    memcpy(associated_report.payload, report->payload, report->payload_len);

  *matched_context = candidate;
  *arbitration_status = aiotf_arbitrate_report(arbitration, &associated_report, now_ms);
  return *arbitration_status <= AIOTF_ARBITRATION_CONFLICT ? AIOTF_DIAGNOSTIC_ASSOCIATED
                                                          : AIOTF_DIAGNOSTIC_ARBITRATION_REJECTED;
}

static aiotf_request_status_t reject_request(aiotf_inventory_session_t *session, aiotf_request_status_t reason)
{
  if (session != NULL) {
    memset(session, 0, sizeof(*session));
    session->result = AIOTF_RESULT_REJECTED;
    session->rejection_reason = reason;
  }
  return reason;
}

aiotf_request_status_t aiotf_inventory_start(aiotf_inventory_context_t *context,
                                             const aiotf_inventory_request_t *request,
                                             uint64_t now_ms,
                                             aiotf_inventory_session_t *session)
{
  if (context == NULL || request == NULL || session == NULL)
    return reject_request(session, AIOTF_REQUEST_INVALID_ARGUMENT);
  if (request->tag_id == 0 || request->tag_id > AIOTF_MAX_TAGS)
    return reject_request(session, AIOTF_REQUEST_INVALID_TAG);
  if (request->timeout_ms == 0)
    return reject_request(session, AIOTF_REQUEST_INVALID_TIMEOUT);
  if (now_ms > UINT64_MAX - request->timeout_ms)
    return reject_request(session, AIOTF_REQUEST_DEADLINE_OVERFLOW);
  if (context->next_correlation_id == 0)
    return reject_request(session, AIOTF_REQUEST_CORRELATION_EXHAUSTED);

  *session = (aiotf_inventory_session_t){
      .correlation_id = context->next_correlation_id,
      .accepted_at_ms = now_ms,
      .deadline_ms = now_ms + request->timeout_ms,
      .tag_id = request->tag_id,
      .result = AIOTF_RESULT_PENDING,
      .rejection_reason = AIOTF_REQUEST_ACCEPTED,
  };
  ++context->next_correlation_id;
  return AIOTF_REQUEST_ACCEPTED;
}

bool aiotf_inventory_expire(aiotf_inventory_session_t *session, uint64_t now_ms)
{
  if (session == NULL || session->result != AIOTF_RESULT_PENDING || now_ms < session->deadline_ms)
    return false;
  session->result = AIOTF_RESULT_TIMEOUT;
  return true;
}

aiotf_report_status_t aiotf_inventory_associate_report(aiotf_inventory_session_t *session,
                                                       const aiotf_inventory_report_t *report,
                                                       uint64_t now_ms)
{
  if (session == NULL || report == NULL)
    return AIOTF_REPORT_INVALID_ARGUMENT;
  if (session->result != AIOTF_RESULT_PENDING)
    return AIOTF_REPORT_NOT_PENDING;
  if (aiotf_inventory_expire(session, now_ms))
    return AIOTF_REPORT_AFTER_TIMEOUT;
  if (report->tag_id != session->tag_id)
    return AIOTF_REPORT_TAG_MISMATCH;
  if (report->reader_handle == 0)
    return AIOTF_REPORT_INVALID_READER;
  if (report->payload_len == 0 || report->payload_len > AIOTF_MAX_PAYLOAD_BYTES)
    return AIOTF_REPORT_INVALID_PAYLOAD_LENGTH;
  if (!report->crc_valid)
    return AIOTF_REPORT_CRC_FAILURE;

  session->report = *report;
  session->has_report = true;
  session->result = AIOTF_RESULT_COMPLETED;
  return AIOTF_REPORT_ACCEPTED;
}
