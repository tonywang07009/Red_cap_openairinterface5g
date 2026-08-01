#include <gtest/gtest.h>

extern "C" {
#include "openair2/RRC/NR_UE/rrc_ue_lowpower.h"
}

TEST(NrRrcLowPower, ClearsEdrxFlagsWhenSib1V1700IsAbsent)
{
  NR_UE_RRC_SI_INFO si_info = {};
  si_info.edrx_allowed_idle_r17 = true;
  si_info.edrx_allowed_inactive_r17 = true;

  nr_rrc_apply_sib1_edrx(&si_info, nullptr);

  EXPECT_FALSE(si_info.edrx_allowed_idle_r17);
  EXPECT_FALSE(si_info.edrx_allowed_inactive_r17);
}

TEST(NrRrcLowPower, StoresIdleAndInactiveEdrxAllowedFlags)
{
  NR_UE_RRC_SI_INFO si_info = {};
  NR_SIB1_v1700_IEs_t sib1_v1700 = {};
  long idle = NR_SIB1_v1700_IEs__eDRX_AllowedIdle_r17_true;
  long inactive = NR_SIB1_v1700_IEs__eDRX_AllowedInactive_r17_true;
  sib1_v1700.eDRX_AllowedIdle_r17 = &idle;
  sib1_v1700.eDRX_AllowedInactive_r17 = &inactive;

  nr_rrc_apply_sib1_edrx(&si_info, &sib1_v1700);

  EXPECT_TRUE(si_info.edrx_allowed_idle_r17);
  EXPECT_TRUE(si_info.edrx_allowed_inactive_r17);
}

TEST(NrRrcLowPower, GatesEdrxByRrcState)
{
  NR_UE_RRC_SI_INFO si_info = {};
  si_info.edrx_allowed_idle_r17 = true;
  si_info.edrx_allowed_inactive_r17 = false;

  EXPECT_TRUE(nr_rrc_edrx_allowed_for_state(&si_info, RRC_STATE_IDLE_NR));
  EXPECT_FALSE(nr_rrc_edrx_allowed_for_state(&si_info, RRC_STATE_INACTIVE_NR));
  EXPECT_FALSE(nr_rrc_edrx_allowed_for_state(&si_info, RRC_STATE_CONNECTED_NR));
}

int main(int argc, char **argv)
{
  testing::InitGoogleTest(&argc, argv);
  return RUN_ALL_TESTS();
}
