#include "aiotf_inventory.h"

#include <assert.h>
#include <limits.h>
#include <stdio.h>

static aiotf_inventory_report_t valid_report(uint32_t tag_id)
{
  return (aiotf_inventory_report_t){
      .tag_id = tag_id,
      .reader_handle = 1,
      .crc_valid = true,
      .payload_len = 4,
      .payload = {1, 2, 3, 4},
  };
}

static void assert_binding(const aiotf_binding_table_t *table,
                           uint32_t tag_id,
                           size_t eligible_count,
                           uint32_t eligible_first,
                           uint32_t eligible_second,
                           uint32_t primary)
{
  const aiotf_reader_binding_t *binding = aiotf_binding_table_get(table, tag_id);
  assert(binding != NULL && binding->tag_id == tag_id);
  assert(binding->eligible_reader_count == eligible_count);
  assert(binding->eligible_readers[0] == eligible_first);
  assert(eligible_count == 1 || binding->eligible_readers[1] == eligible_second);
  assert(binding->default_primary_reader == primary);
  assert(binding->primary_reader == primary);
  assert(binding->binding_epoch == 1);
  assert(binding->resource_policy == AIOTF_RESOURCE_SERIALIZED_SINGLE_TAG);
}

static void test_bounded_binding_profile(void)
{
  aiotf_binding_table_t table;
  assert(!aiotf_binding_table_init(NULL));
  assert(aiotf_binding_table_init(&table));
  assert(aiotf_binding_table_validate_profile(&table));
  assert(aiotf_binding_table_get(&table, 0) == NULL);
  assert(aiotf_binding_table_get(&table, 61) == NULL);

  assert_binding(&table, 1, 1, AIOTF_READER_UE1, 0, AIOTF_READER_UE1);
  assert_binding(&table, 20, 1, AIOTF_READER_UE1, 0, AIOTF_READER_UE1);
  assert_binding(&table, 21, 2, AIOTF_READER_UE1, AIOTF_READER_UE2, AIOTF_READER_UE1);
  assert_binding(&table, 30, 2, AIOTF_READER_UE1, AIOTF_READER_UE2, AIOTF_READER_UE1);
  assert_binding(&table, 31, 2, AIOTF_READER_UE1, AIOTF_READER_UE2, AIOTF_READER_UE2);
  assert_binding(&table, 40, 2, AIOTF_READER_UE1, AIOTF_READER_UE2, AIOTF_READER_UE2);
  assert_binding(&table, 41, 1, AIOTF_READER_UE2, 0, AIOTF_READER_UE2);
  assert_binding(&table, 60, 1, AIOTF_READER_UE2, 0, AIOTF_READER_UE2);

  size_t ue1_primary = 0;
  size_t ue2_primary = 0;
  for (uint32_t tag_id = 1; tag_id <= AIOTF_MAX_TAGS; ++tag_id) {
    const aiotf_reader_binding_t *binding = aiotf_binding_table_get(&table, tag_id);
    ue1_primary += binding->default_primary_reader == AIOTF_READER_UE1;
    ue2_primary += binding->default_primary_reader == AIOTF_READER_UE2;
  }
  assert(ue1_primary == 30 && ue2_primary == 30);
}

static void test_binding_profile_rejects_invalid_state(void)
{
  aiotf_binding_table_t table;
  assert(aiotf_binding_table_init(&table));

  table.bindings[20].eligible_reader_count = 0;
  assert(!aiotf_binding_table_validate_profile(&table));
  assert(aiotf_binding_table_init(&table));
  table.bindings[20].eligible_readers[1] = AIOTF_READER_UE1;
  assert(!aiotf_binding_table_validate_profile(&table));
  assert(aiotf_binding_table_init(&table));
  table.bindings[30].default_primary_reader = 3;
  assert(!aiotf_binding_table_validate_profile(&table));
  assert(aiotf_binding_table_init(&table));
  table.bindings[40].binding_epoch = 0;
  assert(!aiotf_binding_table_validate_profile(&table));
  assert(aiotf_binding_table_init(&table));
  table.bindings[59].tag_id = 59;
  assert(!aiotf_binding_table_validate_profile(&table));
  assert(aiotf_binding_table_init(&table));
  table.bindings[0].resource_policy = 0;
  assert(!aiotf_binding_table_validate_profile(&table));
}

static void test_pre_r2d_failover(void)
{
  aiotf_binding_table_t table;
  assert(aiotf_binding_table_init(&table));
  aiotf_reader_binding_t *shared = &table.bindings[24];
  assert(shared->tag_id == 25 && shared->primary_reader == AIOTF_READER_UE1 && shared->binding_epoch == 1);

  assert(aiotf_failover_primary(shared, false, true, true) == AIOTF_FAILOVER_NOT_NEEDED);
  assert(aiotf_failover_primary(shared, true, false, true) == AIOTF_FAILOVER_AFTER_R2D);
  assert(shared->primary_reader == AIOTF_READER_UE1 && shared->binding_epoch == 1);
  assert(aiotf_failover_primary(shared, false, false, false) == AIOTF_FAILOVER_ALTERNATIVE_UNAVAILABLE);
  assert(aiotf_failover_primary(shared, false, false, true) == AIOTF_FAILOVER_OK);
  assert(shared->default_primary_reader == AIOTF_READER_UE1);
  assert(shared->primary_reader == AIOTF_READER_UE2 && shared->binding_epoch == 2);

  aiotf_reader_selection_t selection;
  assert(aiotf_select_readers(shared, AIOTF_READER_MODE_DIVERSITY, true, true, &selection)
         == AIOTF_READER_SELECTION_OK);
  assert(selection.primary_reader == AIOTF_READER_UE2 && selection.binding_epoch == 2);
  assert(selection.active_roles[0] == AIOTF_READER_ROLE_R2D_PRIMARY);
  assert(selection.active_roles[1] == AIOTF_READER_ROLE_D2R_OBSERVER);

  aiotf_reader_binding_t *exclusive = &table.bindings[19];
  assert(aiotf_failover_primary(exclusive, false, false, true) == AIOTF_FAILOVER_EXCLUSIVE_BINDING);
  assert(exclusive->primary_reader == AIOTF_READER_UE1 && exclusive->binding_epoch == 1);

  shared->binding_epoch = UINT32_MAX;
  assert(aiotf_failover_primary(shared, false, true, false) == AIOTF_FAILOVER_EPOCH_EXHAUSTED);
  assert(shared->primary_reader == AIOTF_READER_UE2 && shared->binding_epoch == UINT32_MAX);
  shared->eligible_reader_count = 0;
  assert(aiotf_failover_primary(shared, false, true, true) == AIOTF_FAILOVER_INVALID_BINDING);
  assert(aiotf_failover_primary(NULL, false, true, true) == AIOTF_FAILOVER_INVALID_ARGUMENT);
}

static void test_reader_selection(void)
{
  aiotf_binding_table_t table;
  assert(aiotf_binding_table_init(&table));
  aiotf_reader_selection_t selection;

  const aiotf_reader_binding_t *tag25 = aiotf_binding_table_get(&table, 25);
  assert(aiotf_select_readers(tag25, AIOTF_READER_MODE_NORMAL, true, true, &selection)
         == AIOTF_READER_SELECTION_OK);
  assert(selection.active_reader_count == 1);
  assert(selection.primary_reader == AIOTF_READER_UE1);
  assert(selection.active_readers[0] == AIOTF_READER_UE1);
  assert(selection.active_roles[0] == AIOTF_READER_ROLE_R2D_PRIMARY);

  assert(aiotf_select_readers(tag25, AIOTF_READER_MODE_DIVERSITY, true, true, &selection)
         == AIOTF_READER_SELECTION_OK);
  assert(selection.active_reader_count == 2);
  assert(selection.active_readers[0] == AIOTF_READER_UE1);
  assert(selection.active_roles[0] == AIOTF_READER_ROLE_R2D_PRIMARY);
  assert(selection.active_readers[1] == AIOTF_READER_UE2);
  assert(selection.active_roles[1] == AIOTF_READER_ROLE_D2R_OBSERVER);

  const aiotf_reader_binding_t *tag35 = aiotf_binding_table_get(&table, 35);
  assert(aiotf_select_readers(tag35, AIOTF_READER_MODE_DIVERSITY, true, true, &selection)
         == AIOTF_READER_SELECTION_OK);
  assert(selection.primary_reader == AIOTF_READER_UE2);
  assert(selection.active_readers[0] == AIOTF_READER_UE2);
  assert(selection.active_readers[1] == AIOTF_READER_UE1);

  assert(aiotf_select_readers(tag25, AIOTF_READER_MODE_DIVERSITY, true, false, &selection)
         == AIOTF_READER_SELECTION_OK);
  assert(selection.active_reader_count == 1 && selection.primary_reader == AIOTF_READER_UE1);
  assert(aiotf_select_readers(tag25, AIOTF_READER_MODE_NORMAL, false, true, &selection)
         == AIOTF_READER_SELECTION_PRIMARY_UNAVAILABLE);

  const aiotf_reader_binding_t *tag20 = aiotf_binding_table_get(&table, 20);
  assert(aiotf_select_readers(tag20, AIOTF_READER_MODE_DIVERSITY, true, true, &selection)
         == AIOTF_READER_SELECTION_DIVERSITY_NOT_ELIGIBLE);
  assert(aiotf_select_readers(NULL, AIOTF_READER_MODE_NORMAL, true, true, &selection)
         == AIOTF_READER_SELECTION_INVALID_ARGUMENT);
  assert(aiotf_select_readers(tag25, (aiotf_reader_mode_t)2, true, true, &selection)
         == AIOTF_READER_SELECTION_INVALID_ARGUMENT);
}

static void test_deterministic_serialization(void)
{
  aiotf_inventory_context_t context;
  aiotf_inventory_context_init(&context);
  aiotf_binding_table_t table;
  assert(aiotf_binding_table_init(&table));
  aiotf_tag_transaction_t transactions[AIOTF_MAX_TAGS];
  size_t count = 99;

  const uint32_t shuffled[] = {40, 1, 21};
  assert(aiotf_schedule_transactions(&context, &table, 7, shuffled, 3, 100, transactions, AIOTF_MAX_TAGS, &count)
         == AIOTF_SCHEDULE_OK);
  assert(count == 3);
  assert(transactions[0].tag_id == 1 && transactions[0].response_slot == 100 && transactions[0].session_id == 1);
  assert(transactions[1].tag_id == 21 && transactions[1].response_slot == 101 && transactions[1].session_id == 2);
  assert(transactions[2].tag_id == 40 && transactions[2].response_slot == 102 && transactions[2].session_id == 3);
  for (size_t i = 0; i < count; ++i) {
    assert(transactions[i].correlation_id == 7);
    assert(transactions[i].binding_epoch == 1);
    assert(transactions[i].result == AIOTF_RESULT_PENDING);
  }

  uint32_t all_tags[AIOTF_MAX_TAGS];
  for (size_t i = 0; i < AIOTF_MAX_TAGS; ++i)
    all_tags[i] = AIOTF_MAX_TAGS - i;
  assert(aiotf_schedule_transactions(
             &context, &table, 8, all_tags, AIOTF_MAX_TAGS, 1000, transactions, AIOTF_MAX_TAGS, &count)
         == AIOTF_SCHEDULE_OK);
  assert(count == AIOTF_MAX_TAGS);
  size_t ue1_primary = 0;
  size_t ue2_primary = 0;
  for (size_t i = 0; i < count; ++i) {
    assert(transactions[i].tag_id == i + 1);
    assert(transactions[i].response_slot == 1000 + i);
    assert(transactions[i].correlation_id == 8);
    assert(transactions[i].session_id == 4 + i);
    assert(transactions[i].binding_epoch == 1);
    assert(transactions[i].result == AIOTF_RESULT_PENDING);
    const aiotf_reader_binding_t *binding = aiotf_binding_table_get(&table, transactions[i].tag_id);
    ue1_primary += binding->primary_reader == AIOTF_READER_UE1;
    ue2_primary += binding->primary_reader == AIOTF_READER_UE2;
  }
  assert(ue1_primary == 30 && ue2_primary == 30);
  printf("AIOTF_SERIALIZED_60_TAGS correlation=8 count=%zu first_tag=%u last_tag=%u first_slot=%llu "
         "last_slot=%llu unique_slots=%zu ue1_primary=%zu ue2_primary=%zu\n",
         count,
         transactions[0].tag_id,
         transactions[count - 1].tag_id,
         (unsigned long long)transactions[0].response_slot,
         (unsigned long long)transactions[count - 1].response_slot,
         count,
         ue1_primary,
         ue2_primary);
}

static void test_serialization_rejects_invalid_input(void)
{
  aiotf_inventory_context_t context;
  aiotf_inventory_context_init(&context);
  aiotf_binding_table_t table;
  assert(aiotf_binding_table_init(&table));
  aiotf_tag_transaction_t transactions[AIOTF_MAX_TAGS];
  size_t count = 99;
  const uint32_t tag1[] = {1};

  assert(aiotf_schedule_transactions(&context, &table, 1, tag1, 0, 0, transactions, AIOTF_MAX_TAGS, &count)
         == AIOTF_SCHEDULE_INVALID_TAG_COUNT);
  assert(count == 0);
  assert(aiotf_schedule_transactions(&context, &table, 1, tag1, 61, 0, transactions, AIOTF_MAX_TAGS, &count)
         == AIOTF_SCHEDULE_INVALID_TAG_COUNT);
  const uint32_t invalid_zero[] = {0};
  assert(aiotf_schedule_transactions(
             &context, &table, 1, invalid_zero, 1, 0, transactions, AIOTF_MAX_TAGS, &count)
         == AIOTF_SCHEDULE_INVALID_TAG);
  const uint32_t invalid_61[] = {61};
  assert(aiotf_schedule_transactions(&context, &table, 1, invalid_61, 1, 0, transactions, AIOTF_MAX_TAGS, &count)
         == AIOTF_SCHEDULE_INVALID_TAG);
  const uint32_t duplicate[] = {1, 1};
  assert(aiotf_schedule_transactions(&context, &table, 1, duplicate, 2, 0, transactions, AIOTF_MAX_TAGS, &count)
         == AIOTF_SCHEDULE_DUPLICATE_TAG);
  assert(aiotf_schedule_transactions(&context, &table, 1, tag1, 1, 0, transactions, 0, &count)
         == AIOTF_SCHEDULE_OUTPUT_TOO_SMALL);
  const uint32_t two_tags[] = {1, 2};
  assert(aiotf_schedule_transactions(
             &context, &table, 1, two_tags, 2, UINT64_MAX, transactions, AIOTF_MAX_TAGS, &count)
         == AIOTF_SCHEDULE_SLOT_OVERFLOW);
  context.next_session_id = UINT64_MAX;
  assert(aiotf_schedule_transactions(&context, &table, 1, tag1, 1, 0, transactions, AIOTF_MAX_TAGS, &count)
         == AIOTF_SCHEDULE_OK);
  assert(transactions[0].session_id == UINT64_MAX && context.next_session_id == 0);
  assert(aiotf_schedule_transactions(&context, &table, 1, tag1, 1, 0, transactions, AIOTF_MAX_TAGS, &count)
         == AIOTF_SCHEDULE_SESSION_EXHAUSTED);
}

static aiotf_inventory_report_t transaction_report(const aiotf_tag_transaction_t *transaction,
                                                   uint32_t reader_handle,
                                                   uint8_t payload_byte)
{
  return (aiotf_inventory_report_t){
      .correlation_id = transaction->correlation_id,
      .session_id = transaction->session_id,
      .tag_id = transaction->tag_id,
      .binding_epoch = transaction->binding_epoch,
      .reader_handle = reader_handle,
      .crc_valid = true,
      .payload_len = 1,
      .payload = {payload_byte},
  };
}

static void prepare_arbitration(aiotf_report_arbitration_t *arbitration,
                                aiotf_reader_mode_t mode,
                                uint64_t deadline_ms)
{
  aiotf_inventory_context_t context;
  aiotf_inventory_context_init(&context);
  aiotf_binding_table_t table;
  assert(aiotf_binding_table_init(&table));
  const aiotf_reader_binding_t *binding = aiotf_binding_table_get(&table, 25);
  aiotf_reader_selection_t selection;
  assert(aiotf_select_readers(binding, mode, true, true, &selection) == AIOTF_READER_SELECTION_OK);
  const uint32_t tag_id[] = {25};
  aiotf_tag_transaction_t transaction;
  size_t count = 0;
  assert(aiotf_schedule_transactions(&context, &table, 9, tag_id, 1, 100, &transaction, 1, &count)
         == AIOTF_SCHEDULE_OK);
  assert(count == 1);
  assert(aiotf_report_arbitration_init(arbitration, &transaction, &selection, deadline_ms));
}

static aiotf_diagnostic_report_t diagnostic_report(uint32_t reader_handle, uint32_t frame, uint32_t slot)
{
  return (aiotf_diagnostic_report_t){
      .reader_handle = reader_handle,
      .tag_id = 25,
      .frame = frame,
      .slot = slot,
      .crc_valid = true,
      .payload_len = 1,
      .payload = {0x11},
  };
}

static void test_diagnostic_pending_context_adapter(void)
{
  aiotf_pending_report_context_t context = {.frame = 10, .slot = 5};
  prepare_arbitration(&context.arbitration, AIOTF_READER_MODE_DIVERSITY, 1000);
  const aiotf_diagnostic_report_t report = diagnostic_report(AIOTF_READER_UE2, 10, 5);
  size_t matched = SIZE_MAX;
  aiotf_arbitration_status_t arbitration_status = AIOTF_ARBITRATION_INVALID_ARGUMENT;
  assert(aiotf_diagnostic_associate_report(&context, 1, &report, 999, &matched, &arbitration_status)
         == AIOTF_DIAGNOSTIC_ASSOCIATED);
  assert(matched == 0 && arbitration_status == AIOTF_ARBITRATION_FIRST_VALID);
  assert(context.arbitration.has_result && context.arbitration.result_report.reader_handle == AIOTF_READER_UE2);

  aiotf_pending_report_context_t ambiguous[2] = {
      {.frame = 10, .slot = 5},
      {.frame = 10, .slot = 5},
  };
  prepare_arbitration(&ambiguous[0].arbitration, AIOTF_READER_MODE_DIVERSITY, 1000);
  ambiguous[1].arbitration = ambiguous[0].arbitration;
  ambiguous[1].arbitration.transaction.correlation_id++;
  ambiguous[1].arbitration.transaction.session_id++;
  matched = 0;
  assert(aiotf_diagnostic_associate_report(ambiguous, 2, &report, 999, &matched, &arbitration_status)
         == AIOTF_DIAGNOSTIC_AMBIGUOUS_CONTEXT);
  assert(matched == SIZE_MAX && arbitration_status == AIOTF_ARBITRATION_INVALID_ARGUMENT);
  assert(!ambiguous[0].arbitration.has_result && !ambiguous[1].arbitration.has_result);

  aiotf_diagnostic_report_t wrong_slot = diagnostic_report(AIOTF_READER_UE2, 10, 6);
  assert(aiotf_diagnostic_associate_report(ambiguous, 2, &wrong_slot, 999, &matched, &arbitration_status)
         == AIOTF_DIAGNOSTIC_NO_PENDING_CONTEXT);

  aiotf_pending_report_context_t normal = {.frame = 10, .slot = 5};
  prepare_arbitration(&normal.arbitration, AIOTF_READER_MODE_NORMAL, 1000);
  assert(aiotf_diagnostic_associate_report(&normal, 1, &report, 999, &matched, &arbitration_status)
         == AIOTF_DIAGNOSTIC_ARBITRATION_REJECTED);
  assert(arbitration_status == AIOTF_ARBITRATION_INACTIVE_READER && !normal.arbitration.has_result);
}

static void test_first_valid_duplicate_and_conflict(void)
{
  aiotf_report_arbitration_t arbitration;
  prepare_arbitration(&arbitration, AIOTF_READER_MODE_DIVERSITY, 1000);

  aiotf_inventory_report_t report = transaction_report(&arbitration.transaction, AIOTF_READER_UE2, 0x11);
  assert(aiotf_arbitrate_report(&arbitration, &report, 999) == AIOTF_ARBITRATION_FIRST_VALID);
  assert(arbitration.has_result && arbitration.transaction.result == AIOTF_RESULT_COMPLETED);
  assert(arbitration.result_report.reader_handle == AIOTF_READER_UE2);

  report.reader_handle = AIOTF_READER_UE1;
  assert(aiotf_arbitrate_report(&arbitration, &report, 999) == AIOTF_ARBITRATION_DUPLICATE);
  assert(arbitration.duplicate_report_count == 1 && arbitration.evidence_count == 1);
  report.payload[0] = 0x22;
  assert(aiotf_arbitrate_report(&arbitration, &report, 999) == AIOTF_ARBITRATION_CONFLICT);
  assert(arbitration.conflicting_valid_reports && arbitration.conflict_report_count == 1);
  assert(arbitration.result_report.payload[0] == 0x11);
  assert(arbitration.evidence[0].kind == AIOTF_EVIDENCE_DUPLICATE);
  assert(arbitration.evidence[1].kind == AIOTF_EVIDENCE_CONFLICT);
}

static void test_arbitration_rejects_invalid_reports(void)
{
  aiotf_report_arbitration_t arbitration;
  prepare_arbitration(&arbitration, AIOTF_READER_MODE_NORMAL, 1000);
  const aiotf_tag_transaction_t transaction = arbitration.transaction;
  aiotf_inventory_report_t report = transaction_report(&transaction, AIOTF_READER_UE1, 1);

  report.correlation_id++;
  assert(aiotf_arbitrate_report(&arbitration, &report, 999) == AIOTF_ARBITRATION_INVALID_CORRELATION);
  report = transaction_report(&transaction, AIOTF_READER_UE1, 1);
  report.session_id++;
  assert(aiotf_arbitrate_report(&arbitration, &report, 999) == AIOTF_ARBITRATION_INVALID_SESSION);
  report = transaction_report(&transaction, AIOTF_READER_UE1, 1);
  report.tag_id++;
  assert(aiotf_arbitrate_report(&arbitration, &report, 999) == AIOTF_ARBITRATION_INVALID_TAG);
  report = transaction_report(&transaction, AIOTF_READER_UE1, 1);
  report.binding_epoch++;
  assert(aiotf_arbitrate_report(&arbitration, &report, 999) == AIOTF_ARBITRATION_STALE_EPOCH);
  report = transaction_report(&transaction, AIOTF_READER_UE2, 1);
  assert(aiotf_arbitrate_report(&arbitration, &report, 999) == AIOTF_ARBITRATION_INACTIVE_READER);
  report = transaction_report(&transaction, AIOTF_READER_UE1, 1);
  report.crc_valid = false;
  assert(aiotf_arbitrate_report(&arbitration, &report, 999) == AIOTF_ARBITRATION_CRC_FAILURE);
  report = transaction_report(&transaction, AIOTF_READER_UE1, 1);
  report.payload_len = 0;
  assert(aiotf_arbitrate_report(&arbitration, &report, 999) == AIOTF_ARBITRATION_INVALID_PAYLOAD_LENGTH);
  report = transaction_report(&transaction, AIOTF_READER_UE1, 1);
  assert(aiotf_arbitrate_report(&arbitration, &report, 1000) == AIOTF_ARBITRATION_AFTER_DEADLINE);
  assert(arbitration.invalid_report_count == 8);
  assert(arbitration.stale_epoch_report_count == 1);
  assert(arbitration.evidence_count == AIOTF_MAX_REPORT_EVIDENCE);
  assert(!arbitration.has_result && arbitration.transaction.result == AIOTF_RESULT_TIMEOUT);

  report.correlation_id++;
  assert(aiotf_arbitrate_report(&arbitration, &report, 1001) == AIOTF_ARBITRATION_INVALID_CORRELATION);
  assert(arbitration.evidence_dropped == 1);
}

static void test_arbitration_timeout_boundaries(void)
{
  assert(!aiotf_report_arbitration_init(NULL, NULL, NULL, 0));
  assert(aiotf_arbitrate_report(NULL, NULL, 0) == AIOTF_ARBITRATION_INVALID_ARGUMENT);
  aiotf_report_arbitration_t arbitration;
  prepare_arbitration(&arbitration, AIOTF_READER_MODE_NORMAL, 1000);
  assert(!aiotf_report_arbitration_expire(&arbitration, 999));
  assert(aiotf_report_arbitration_expire(&arbitration, 1000));
  assert(arbitration.transaction.result == AIOTF_RESULT_TIMEOUT);
  assert(!aiotf_report_arbitration_expire(&arbitration, 1001));
}

static void test_failover_report_race(void)
{
  aiotf_inventory_context_t context;
  aiotf_inventory_context_init(&context);
  aiotf_binding_table_t table;
  assert(aiotf_binding_table_init(&table));
  aiotf_reader_binding_t *binding = &table.bindings[24];
  aiotf_reader_selection_t old_selection;
  assert(aiotf_select_readers(binding, AIOTF_READER_MODE_NORMAL, true, true, &old_selection)
         == AIOTF_READER_SELECTION_OK);

  const uint32_t tag_id[] = {25};
  aiotf_tag_transaction_t old_transaction;
  size_t count = 0;
  assert(aiotf_schedule_transactions(&context, &table, 10, tag_id, 1, 100, &old_transaction, 1, &count)
         == AIOTF_SCHEDULE_OK);
  assert(aiotf_failover_primary(binding, false, false, true) == AIOTF_FAILOVER_OK);

  aiotf_reader_selection_t new_selection;
  assert(aiotf_select_readers(binding, AIOTF_READER_MODE_NORMAL, false, true, &new_selection)
         == AIOTF_READER_SELECTION_OK);
  aiotf_tag_transaction_t new_transaction;
  assert(aiotf_schedule_transactions(&context, &table, 10, tag_id, 1, 101, &new_transaction, 1, &count)
         == AIOTF_SCHEDULE_OK);
  assert(old_transaction.binding_epoch == 1 && new_transaction.binding_epoch == 2);
  assert(old_transaction.session_id != new_transaction.session_id);

  aiotf_report_arbitration_t arbitration;
  assert(aiotf_report_arbitration_init(&arbitration, &new_transaction, &new_selection, 1000));
  aiotf_inventory_report_t old_report = transaction_report(&old_transaction, AIOTF_READER_UE1, 1);
  assert(aiotf_arbitrate_report(&arbitration, &old_report, 999) == AIOTF_ARBITRATION_INVALID_SESSION);
  old_report.session_id = new_transaction.session_id;
  assert(aiotf_arbitrate_report(&arbitration, &old_report, 999) == AIOTF_ARBITRATION_STALE_EPOCH);

  const aiotf_inventory_report_t new_report = transaction_report(&new_transaction, AIOTF_READER_UE2, 1);
  assert(aiotf_arbitrate_report(&arbitration, &new_report, 999) == AIOTF_ARBITRATION_FIRST_VALID);
  assert(arbitration.result_report.reader_handle == AIOTF_READER_UE2);
  assert(arbitration.invalid_report_count == 2 && arbitration.stale_epoch_report_count == 1);
}

static void test_request_validation(void)
{
  aiotf_inventory_context_t context;
  aiotf_inventory_context_init(&context);
  aiotf_inventory_session_t session;

  assert(aiotf_inventory_start(NULL, NULL, 0, NULL) == AIOTF_REQUEST_INVALID_ARGUMENT);
  assert(aiotf_inventory_start(&context, &(aiotf_inventory_request_t){.tag_id = 0, .timeout_ms = 100}, 0, &session)
         == AIOTF_REQUEST_INVALID_TAG);
  assert(session.result == AIOTF_RESULT_REJECTED && session.correlation_id == 0);
  assert(aiotf_inventory_start(&context, &(aiotf_inventory_request_t){.tag_id = 1, .timeout_ms = 0}, 0, &session)
         == AIOTF_REQUEST_INVALID_TIMEOUT);
  assert(aiotf_inventory_start(&context, &(aiotf_inventory_request_t){.tag_id = 61, .timeout_ms = 100}, 0, &session)
         == AIOTF_REQUEST_INVALID_TAG);
  assert(aiotf_inventory_start(&context,
                               &(aiotf_inventory_request_t){.tag_id = 60, .timeout_ms = 2},
                               UINT64_MAX - 1,
                               &session)
         == AIOTF_REQUEST_DEADLINE_OVERFLOW);

  context.next_correlation_id = 0;
  assert(aiotf_inventory_start(&context, &(aiotf_inventory_request_t){.tag_id = 1, .timeout_ms = 100}, 0, &session)
         == AIOTF_REQUEST_CORRELATION_EXHAUSTED);

  context.next_correlation_id = UINT64_MAX;
  assert(aiotf_inventory_start(&context, &(aiotf_inventory_request_t){.tag_id = 1, .timeout_ms = 1}, 0, &session)
         == AIOTF_REQUEST_ACCEPTED);
  assert(session.correlation_id == UINT64_MAX && context.next_correlation_id == 0);
  assert(aiotf_inventory_start(&context, &(aiotf_inventory_request_t){.tag_id = 1, .timeout_ms = 1}, 0, &session)
         == AIOTF_REQUEST_CORRELATION_EXHAUSTED);
}

static void test_correlation_and_completion(void)
{
  aiotf_inventory_context_t context;
  aiotf_inventory_context_init(&context);
  aiotf_inventory_session_t first;
  aiotf_inventory_session_t second;
  const aiotf_inventory_request_t request = {.tag_id = 1, .timeout_ms = 100};

  assert(aiotf_inventory_start(&context, &request, 1000, &first) == AIOTF_REQUEST_ACCEPTED);
  assert(aiotf_inventory_start(&context, &request, 2000, &second) == AIOTF_REQUEST_ACCEPTED);
  assert(first.correlation_id == 1 && second.correlation_id == 2);
  assert(first.result == AIOTF_RESULT_PENDING && first.deadline_ms == 1100);

  const aiotf_inventory_report_t report = valid_report(1);
  assert(aiotf_inventory_associate_report(&first, &report, 1099) == AIOTF_REPORT_ACCEPTED);
  assert(first.result == AIOTF_RESULT_COMPLETED && first.has_report);
  assert(first.report.payload_len == 4 && first.report.payload[3] == 4);
  assert(aiotf_inventory_associate_report(&first, &report, 1099) == AIOTF_REPORT_NOT_PENDING);
}

static void test_report_rejection_and_timeout(void)
{
  aiotf_inventory_context_t context;
  aiotf_inventory_context_init(&context);
  const aiotf_inventory_request_t request = {.tag_id = 20, .timeout_ms = 100};
  aiotf_inventory_session_t session;
  assert(aiotf_inventory_start(&context, &request, 1000, &session) == AIOTF_REQUEST_ACCEPTED);

  aiotf_inventory_report_t report = valid_report(21);
  assert(aiotf_inventory_associate_report(&session, &report, 1099) == AIOTF_REPORT_TAG_MISMATCH);
  report.tag_id = 20;
  report.reader_handle = 0;
  assert(aiotf_inventory_associate_report(&session, &report, 1099) == AIOTF_REPORT_INVALID_READER);
  report.reader_handle = 1;
  report.payload_len = 0;
  assert(aiotf_inventory_associate_report(&session, &report, 1099) == AIOTF_REPORT_INVALID_PAYLOAD_LENGTH);
  report.payload_len = AIOTF_MAX_PAYLOAD_BYTES + 1;
  assert(aiotf_inventory_associate_report(&session, &report, 1099) == AIOTF_REPORT_INVALID_PAYLOAD_LENGTH);
  report.payload_len = 1;
  report.crc_valid = false;
  assert(aiotf_inventory_associate_report(&session, &report, 1099) == AIOTF_REPORT_CRC_FAILURE);
  assert(session.result == AIOTF_RESULT_PENDING && !session.has_report);

  const aiotf_inventory_report_t valid = valid_report(20);
  assert(aiotf_inventory_associate_report(&session, &valid, 1100) == AIOTF_REPORT_AFTER_TIMEOUT);
  assert(session.result == AIOTF_RESULT_TIMEOUT && session.correlation_id == 1);
  assert(!aiotf_inventory_expire(&session, 1101));
}

static void test_timeout_boundaries(void)
{
  aiotf_inventory_context_t context;
  aiotf_inventory_context_init(&context);
  const aiotf_inventory_request_t request = {.tag_id = 60, .timeout_ms = 100};
  aiotf_inventory_session_t before;
  aiotf_inventory_session_t at;
  aiotf_inventory_session_t after;

  assert(aiotf_inventory_start(&context, &request, 1000, &before) == AIOTF_REQUEST_ACCEPTED);
  assert(!aiotf_inventory_expire(&before, 1099));
  assert(before.result == AIOTF_RESULT_PENDING);
  assert(aiotf_inventory_start(&context, &request, 1000, &at) == AIOTF_REQUEST_ACCEPTED);
  assert(aiotf_inventory_expire(&at, 1100) && at.result == AIOTF_RESULT_TIMEOUT);
  assert(aiotf_inventory_start(&context, &request, 1000, &after) == AIOTF_REQUEST_ACCEPTED);
  assert(aiotf_inventory_expire(&after, 1101) && after.result == AIOTF_RESULT_TIMEOUT);
}

int main(void)
{
  test_bounded_binding_profile();
  test_binding_profile_rejects_invalid_state();
  test_pre_r2d_failover();
  test_reader_selection();
  test_deterministic_serialization();
  test_serialization_rejects_invalid_input();
  test_diagnostic_pending_context_adapter();
  test_first_valid_duplicate_and_conflict();
  test_arbitration_rejects_invalid_reports();
  test_arbitration_timeout_boundaries();
  test_failover_report_race();
  test_request_validation();
  test_correlation_and_completion();
  test_report_rejection_and_timeout();
  test_timeout_boundaries();
  puts("AIOTF_INVENTORY_TEST PASS");
  return 0;
}
