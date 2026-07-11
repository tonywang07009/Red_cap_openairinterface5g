#include <gtest/gtest.h>

extern "C" {
#include "openair2/LAYER2/NR_MAC_UE/nr_ue_drx.h"
}

TEST(NrUeDrx, UnconfiguredDrxKeepsUeActive)
{
  nr_drx_config_t drx = {};
  EXPECT_TRUE(nr_ue_drx_is_active_slot(&drx, 1234, false));
}

TEST(NrUeDrx, LongCycleOnDurationControlsActiveWindow)
{
  nr_drx_config_t drx = {};
  drx.configured = true;
  drx.on_duration_slots = 4;
  drx.long_cycle_slots = 20;
  drx.long_cycle_offset_slots = 2;

  EXPECT_FALSE(nr_ue_drx_is_active_slot(&drx, 1, false));
  EXPECT_TRUE(nr_ue_drx_is_active_slot(&drx, 2, false));
  EXPECT_TRUE(nr_ue_drx_is_active_slot(&drx, 5, false));
  EXPECT_FALSE(nr_ue_drx_is_active_slot(&drx, 6, false));
  EXPECT_TRUE(nr_ue_drx_is_active_slot(&drx, 22, false));
}

TEST(NrUeDrx, PendingSrAndInactivityKeepUeActive)
{
  nr_drx_config_t drx = {};
  drx.configured = true;
  drx.on_duration_slots = 1;
  drx.long_cycle_slots = 20;
  drx.active_until_slot = 10;

  EXPECT_TRUE(nr_ue_drx_is_active_slot(&drx, 6, false));
  EXPECT_FALSE(nr_ue_drx_is_active_slot(&drx, 10, false));
  EXPECT_TRUE(nr_ue_drx_is_active_slot(&drx, 10, true));
}

TEST(NrUeDrx, NewAssignmentExtendsActiveTimeByInactivityTimer)
{
  NR_UE_MAC_INST_t mac = {};
  mac.frame_structure.numb_slots_frame = 20;
  mac.scheduling_info.drx_config.configured = true;
  mac.scheduling_info.drx_config.inactivity_slots = 8;

  nr_ue_drx_on_dl_assignment(&mac, 3, 4, 2, true);
  EXPECT_EQ(73U, mac.scheduling_info.drx_config.active_until_slot);
  nr_ue_drx_on_dl_assignment(&mac, 3, 5, 2, false);
  EXPECT_EQ(73U, mac.scheduling_info.drx_config.active_until_slot);
}

TEST(NrUeDrx, UnwrapsSlotAcrossSfnBoundary)
{
  nr_drx_config_t drx = {};
  EXPECT_EQ(10239U, nr_ue_drx_unwrap_slot(&drx, 10, 1023, 9));
  EXPECT_EQ(10240U, nr_ue_drx_unwrap_slot(&drx, 10, 0, 0));
}

TEST(NrUeDrx, NackActivatesHarqRetransmissionWindowAfterRtt)
{
  NR_UE_MAC_INST_t mac = {};
  mac.frame_structure.numb_slots_frame = 10;
  nr_drx_config_t *drx = &mac.scheduling_info.drx_config;
  drx->configured = true;
  drx->long_cycle_slots = 100;
  drx->on_duration_slots = 1;
  drx->harq_rtt_dl_slots = 4;
  drx->retransmission_dl_slots = 8;

  nr_ue_drx_on_dl_harq_feedback(&mac, 1, 0, 3, false);
  EXPECT_FALSE(nr_ue_drx_is_active_slot(drx, 14, false));
  EXPECT_TRUE(nr_ue_drx_is_active_slot(drx, 15, false));
  EXPECT_FALSE(nr_ue_drx_is_active_slot(drx, 23, false));
}

TEST(NrUeDrx, DrxCommandsStopInactivityAndSelectCycle)
{
  NR_UE_MAC_INST_t mac = {};
  mac.frame_structure.numb_slots_frame = 10;
  nr_drx_config_t *drx = &mac.scheduling_info.drx_config;
  drx->configured = true;
  drx->long_cycle_slots = 320;
  drx->on_duration_slots = 10;
  drx->inactivity_slots = 20;
  drx->short_cycle_configured = true;
  drx->short_cycle_slots = 20;
  drx->short_cycle_timer = 2;

  nr_ue_drx_on_dl_assignment(&mac, 0, 2, 0, true);
  ASSERT_GT(drx->active_until_slot, 0U);
  nr_ue_drx_on_command(&mac, 0, 3, false);
  EXPECT_EQ(0U, drx->active_until_slot);
  EXPECT_TRUE(drx->short_cycle_active);

  nr_ue_drx_on_command(&mac, 0, 4, true);
  EXPECT_FALSE(drx->short_cycle_active);
}

TEST(NrUeDrx, DetectsPendingSchedulingRequest)
{
  NR_UE_SCHEDULING_INFO sched_info = {};
  EXPECT_FALSE(nr_ue_drx_has_pending_sr(&sched_info));

  sched_info.sr_info[1].active_SR_ID = true;
  sched_info.sr_info[1].pending = true;
  EXPECT_TRUE(nr_ue_drx_has_pending_sr(&sched_info));
}

TEST(NrUeDrx, CountsAndResetsActiveTimeMetrics)
{
  NR_UE_MAC_INST_t mac = {};
  mac.frame_structure.numb_slots_frame = 10;
  nr_drx_config_t *drx = &mac.scheduling_info.drx_config;
  drx->configured = true;
  drx->long_cycle_slots = 10;
  drx->on_duration_slots = 2;

  for (int slot = 0; slot < 10; ++slot)
    nr_ue_drx_is_active(&mac, 0, slot);

  uint32_t observed_slots = 0;
  uint32_t active_slots = 0;
  nr_ue_drx_get_metrics(&mac.scheduling_info, false, &observed_slots, &active_slots);
  EXPECT_EQ(10U, observed_slots);
  EXPECT_EQ(2U, active_slots);

  nr_ue_drx_get_metrics(&mac.scheduling_info, true, &observed_slots, &active_slots);
  EXPECT_EQ(10U, observed_slots);
  EXPECT_EQ(2U, active_slots);
  nr_ue_drx_get_metrics(&mac.scheduling_info, false, &observed_slots, &active_slots);
  EXPECT_EQ(0U, observed_slots);
  EXPECT_EQ(0U, active_slots);
}

int main(int argc, char **argv)
{
  testing::InitGoogleTest(&argc, argv);
  return RUN_ALL_TESTS();
}
