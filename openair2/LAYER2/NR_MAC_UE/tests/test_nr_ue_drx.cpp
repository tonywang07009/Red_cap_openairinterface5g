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

TEST(NrUeDrx, ActivityExtendsActiveTimeByInactivityTimer)
{
  NR_UE_MAC_INST_t mac = {};
  mac.frame_structure.numb_slots_frame = 20;
  mac.scheduling_info.drx_config.configured = true;
  mac.scheduling_info.drx_config.inactivity_slots = 8;

  nr_ue_drx_note_activity(&mac, 3, 4);
  EXPECT_EQ(72U, mac.scheduling_info.drx_config.active_until_slot);
}

TEST(NrUeDrx, DetectsPendingSchedulingRequest)
{
  NR_UE_SCHEDULING_INFO sched_info = {};
  EXPECT_FALSE(nr_ue_drx_has_pending_sr(&sched_info));

  sched_info.sr_info[1].active_SR_ID = true;
  sched_info.sr_info[1].pending = true;
  EXPECT_TRUE(nr_ue_drx_has_pending_sr(&sched_info));
}

int main(int argc, char **argv)
{
  testing::InitGoogleTest(&argc, argv);
  return RUN_ALL_TESTS();
}
