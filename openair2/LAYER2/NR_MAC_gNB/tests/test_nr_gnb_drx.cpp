/*
 * Licensed to the OpenAirInterface (OAI) Software Alliance under one or more
 * contributor license agreements. See the NOTICE file distributed with this
 * work for additional information regarding copyright ownership.
 */

#include <gtest/gtest.h>

extern "C" {
#include "openair2/LAYER2/NR_MAC_gNB/nr_mac_drx.h"
}

static nr_gnb_drx_profile_t profile(uint32_t version, bool command_enabled = false)
{
  return {
      .policy_version = version,
      .long_cycle_ms = 320,
      .on_duration_ms = 10,
      .inactivity_ms = 20,
      .start_offset_ms = 0,
      .drx_command_enabled = command_enabled,
  };
}

TEST(nr_gnb_drx, gates_outside_on_duration_and_extends_active_time)
{
  nr_gnb_drx_state_t state = {};
  const nr_gnb_drx_profile_t p = profile(1);
  ASSERT_TRUE(nr_gnb_drx_stage_profile(&state, &p));
  ASSERT_TRUE(nr_gnb_drx_commit_profile(&state, 0, 0, 10));

  EXPECT_TRUE(nr_gnb_drx_is_active(&state, 0, 5, 10, false));
  EXPECT_FALSE(nr_gnb_drx_is_active(&state, 1, 0, 10, false));
  nr_gnb_drx_note_new_transmission(&state, 1, 0, 10);
  EXPECT_TRUE(nr_gnb_drx_is_active(&state, 2, 9, 10, false));
  EXPECT_TRUE(nr_gnb_drx_is_active(&state, 3, 0, 10, false));
  EXPECT_FALSE(nr_gnb_drx_is_active(&state, 3, 1, 10, false));
}

TEST(nr_gnb_drx, extends_clock_across_sfn_wrap)
{
  nr_gnb_drx_state_t state = {};
  const nr_gnb_drx_profile_t p = profile(1);
  ASSERT_TRUE(nr_gnb_drx_stage_profile(&state, &p));
  ASSERT_TRUE(nr_gnb_drx_commit_profile(&state, 1023, 9, 10));
  const uint64_t before = state.absolute_slot;

  (void)nr_gnb_drx_is_active(&state, 0, 0, 10, false);
  EXPECT_EQ(before + 1, state.absolute_slot);
}

TEST(nr_gnb_drx, rejects_stale_policy_and_unapproved_profile)
{
  nr_gnb_drx_state_t state = {};
  nr_gnb_drx_profile_t p = profile(4);
  ASSERT_TRUE(nr_gnb_drx_stage_profile(&state, &p));
  ASSERT_TRUE(nr_gnb_drx_commit_profile(&state, 0, 0, 10));

  p.policy_version = 3;
  EXPECT_FALSE(nr_gnb_drx_stage_profile(&state, &p));
  p.policy_version = 5;
  p.long_cycle_ms = 1000;
  EXPECT_FALSE(nr_gnb_drx_stage_profile(&state, &p));
}

TEST(nr_gnb_drx, command_requires_explicit_enable_ack_and_no_pending_work)
{
  nr_gnb_drx_state_t state = {};
  const nr_gnb_drx_profile_t p = profile(1, true);
  ASSERT_TRUE(nr_gnb_drx_stage_profile(&state, &p));
  ASSERT_TRUE(nr_gnb_drx_commit_profile(&state, 0, 0, 10));
  ASSERT_TRUE(nr_gnb_drx_complete_reconfiguration(&state));
  nr_gnb_drx_note_new_transmission(&state, 0, 2, 10);
  nr_gnb_drx_note_dl_ack(&state);
  EXPECT_FALSE(state.drx_command_pending);
  ASSERT_TRUE(nr_gnb_drx_request_command(&state));
  EXPECT_FALSE(nr_gnb_drx_request_command(&state));
  nr_gnb_drx_note_dl_ack(&state);

  EXPECT_FALSE(nr_gnb_drx_take_command(&state, true, false, true));
  EXPECT_FALSE(nr_gnb_drx_take_command(&state, false, false, false));
  EXPECT_TRUE(nr_gnb_drx_take_command(&state, false, false, true));
  EXPECT_EQ(state.absolute_slot, state.active_until_slot);
  EXPECT_FALSE(nr_gnb_drx_take_command(&state, false, false, true));
  nr_gnb_drx_note_new_transmission(&state, 0, 3, 10);
  nr_gnb_drx_note_dl_ack(&state);
  EXPECT_FALSE(state.drx_command_pending);
}

TEST(nr_gnb_drx, harq_retransmission_active_time_is_finite)
{
  nr_gnb_drx_state_t state = {};
  const nr_gnb_drx_profile_t p = profile(1);
  ASSERT_TRUE(nr_gnb_drx_stage_profile(&state, &p));
  ASSERT_TRUE(nr_gnb_drx_commit_profile(&state, 0, 0, 10));
  ASSERT_TRUE(nr_gnb_drx_complete_reconfiguration(&state));

  nr_gnb_drx_note_dl_harq_result(&state, 3, false, 1, 0, 10);
  EXPECT_TRUE(nr_gnb_drx_is_active(&state, 1, 1, 10, false));
  EXPECT_TRUE(nr_gnb_drx_is_active(&state, 1, 8, 10, false));
  EXPECT_FALSE(nr_gnb_drx_is_active(&state, 1, 9, 10, false));

  nr_gnb_drx_note_dl_harq_result(&state, 3, true, 1, 9, 10);
  EXPECT_FALSE(nr_gnb_drx_is_active(&state, 2, 0, 10, false));
}

TEST(nr_gnb_drx, retains_previous_profile_for_rollback)
{
  nr_gnb_drx_state_t state = {};
  nr_gnb_drx_profile_t first = profile(1);
  ASSERT_TRUE(nr_gnb_drx_stage_profile(&state, &first));
  ASSERT_TRUE(nr_gnb_drx_commit_profile(&state, 0, 0, 10));
  ASSERT_TRUE(nr_gnb_drx_complete_reconfiguration(&state));

  nr_gnb_drx_profile_t second = first;
  second.policy_version = 2;
  second.long_cycle_ms = 640;
  ASSERT_TRUE(nr_gnb_drx_stage_profile(&state, &second));
  ASSERT_TRUE(nr_gnb_drx_commit_profile(&state, 1, 0, 10));
  ASSERT_TRUE(state.previous_config_valid);
  EXPECT_EQ(1U, state.previous.policy_version);
  EXPECT_EQ(320U, state.previous.long_cycle_ms);

  EXPECT_FALSE(nr_gnb_drx_stage_profile(&state, &second));
  ASSERT_TRUE(nr_gnb_drx_fail_reconfiguration(&state, 10));
  EXPECT_EQ(1U, state.applied.policy_version);
  EXPECT_EQ(320U, state.applied.long_cycle_ms);
  EXPECT_EQ(2U, state.latest_policy_version);

  second.policy_version = 2;
  EXPECT_FALSE(nr_gnb_drx_stage_profile(&state, &second));
  second.policy_version = 3;
  EXPECT_TRUE(nr_gnb_drx_stage_profile(&state, &second));
}

TEST(nr_gnb_drx, cancels_uncommitted_profile_on_rrc_failure)
{
  nr_gnb_drx_state_t state = {};
  nr_gnb_drx_profile_t first = profile(1);
  ASSERT_TRUE(nr_gnb_drx_stage_profile(&state, &first));
  ASSERT_TRUE(nr_gnb_drx_commit_profile(&state, 0, 0, 10));
  ASSERT_TRUE(nr_gnb_drx_complete_reconfiguration(&state));

  nr_gnb_drx_profile_t second = first;
  second.policy_version = 2;
  second.long_cycle_ms = 640;
  ASSERT_TRUE(nr_gnb_drx_stage_profile(&state, &second));
  ASSERT_TRUE(nr_gnb_drx_fail_reconfiguration(&state, 10));
  EXPECT_EQ(1U, state.applied.policy_version);
  EXPECT_FALSE(state.pending_config_valid);
  EXPECT_FALSE(state.rrc_completion_pending);
}

int main(int argc, char **argv)
{
  testing::InitGoogleTest(&argc, argv);
  return RUN_ALL_TESTS();
}
