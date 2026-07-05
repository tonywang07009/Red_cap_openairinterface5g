#include <cstdlib>

#include <gtest/gtest.h>

extern "C" {
#include "../nr_ue_redcap_bwp.h"
}

TEST(NrUeRedcapBwp, UsesCommonBwpsForNonRedCapUe)
{
  NR_ServingCellConfigCommonSIB_t scc = {};
  NR_BWP_DownlinkCommon_t redcap_dl = {};
  NR_BWP_UplinkCommon_t common_ul = {};
  NR_BWP_UplinkCommon_t redcap_ul = {};

  scc.downlinkConfigCommon.ext1 = (decltype(scc.downlinkConfigCommon.ext1))calloc(1, sizeof(*scc.downlinkConfigCommon.ext1));
  ASSERT_NE(scc.downlinkConfigCommon.ext1, nullptr);
  scc.downlinkConfigCommon.ext1->initialDownlinkBWP_RedCap_r17 = &redcap_dl;

  scc.uplinkConfigCommon = (decltype(scc.uplinkConfigCommon))calloc(1, sizeof(*scc.uplinkConfigCommon));
  ASSERT_NE(scc.uplinkConfigCommon, nullptr);
  scc.uplinkConfigCommon->initialUplinkBWP = common_ul;

  scc.ext2 = (decltype(scc.ext2))calloc(1, sizeof(*scc.ext2));
  ASSERT_NE(scc.ext2, nullptr);
  scc.ext2->uplinkConfigCommon_v1700 =
      (decltype(scc.ext2->uplinkConfigCommon_v1700))calloc(1, sizeof(*scc.ext2->uplinkConfigCommon_v1700));
  ASSERT_NE(scc.ext2->uplinkConfigCommon_v1700, nullptr);
  scc.ext2->uplinkConfigCommon_v1700->initialUplinkBWP_RedCap_r17 = &redcap_ul;

  EXPECT_EQ(&scc.downlinkConfigCommon.initialDownlinkBWP, nr_ue_get_sib1_initial_dl_bwp(&scc, false));
  EXPECT_EQ(&scc.uplinkConfigCommon->initialUplinkBWP, nr_ue_get_sib1_initial_ul_bwp(&scc, false));

  free(scc.ext2->uplinkConfigCommon_v1700);
  free(scc.ext2);
  free(scc.uplinkConfigCommon);
  free(scc.downlinkConfigCommon.ext1);
}

TEST(NrUeRedcapBwp, UsesRedCapBwpsForRedCapUeWhenPresent)
{
  NR_ServingCellConfigCommonSIB_t scc = {};
  NR_BWP_DownlinkCommon_t redcap_dl = {};
  NR_BWP_UplinkCommon_t redcap_ul = {};

  scc.downlinkConfigCommon.ext1 = (decltype(scc.downlinkConfigCommon.ext1))calloc(1, sizeof(*scc.downlinkConfigCommon.ext1));
  ASSERT_NE(scc.downlinkConfigCommon.ext1, nullptr);
  scc.downlinkConfigCommon.ext1->initialDownlinkBWP_RedCap_r17 = &redcap_dl;

  scc.uplinkConfigCommon = (decltype(scc.uplinkConfigCommon))calloc(1, sizeof(*scc.uplinkConfigCommon));
  ASSERT_NE(scc.uplinkConfigCommon, nullptr);

  scc.ext2 = (decltype(scc.ext2))calloc(1, sizeof(*scc.ext2));
  ASSERT_NE(scc.ext2, nullptr);
  scc.ext2->uplinkConfigCommon_v1700 =
      (decltype(scc.ext2->uplinkConfigCommon_v1700))calloc(1, sizeof(*scc.ext2->uplinkConfigCommon_v1700));
  ASSERT_NE(scc.ext2->uplinkConfigCommon_v1700, nullptr);
  scc.ext2->uplinkConfigCommon_v1700->initialUplinkBWP_RedCap_r17 = &redcap_ul;

  EXPECT_EQ(&redcap_dl, nr_ue_get_sib1_initial_dl_bwp(&scc, true));
  EXPECT_EQ(&redcap_ul, nr_ue_get_sib1_initial_ul_bwp(&scc, true));

  free(scc.ext2->uplinkConfigCommon_v1700);
  free(scc.ext2);
  free(scc.uplinkConfigCommon);
  free(scc.downlinkConfigCommon.ext1);
}

TEST(NrUeRedcapBwp, FallsBackToCommonUplinkWhenRedCapUplinkIsAbsent)
{
  NR_ServingCellConfigCommonSIB_t scc = {};
  NR_BWP_UplinkCommon_t common_ul = {};

  scc.uplinkConfigCommon = (decltype(scc.uplinkConfigCommon))calloc(1, sizeof(*scc.uplinkConfigCommon));
  ASSERT_NE(scc.uplinkConfigCommon, nullptr);
  scc.uplinkConfigCommon->initialUplinkBWP = common_ul;

  EXPECT_EQ(&scc.uplinkConfigCommon->initialUplinkBWP, nr_ue_get_sib1_initial_ul_bwp(&scc, true));

  free(scc.uplinkConfigCommon);
}

int main(int argc, char **argv)
{
  testing::InitGoogleTest(&argc, argv);
  return RUN_ALL_TESTS();
}
