#include <cstdlib>

#include <gtest/gtest.h>

extern "C" {
#include "NR_RedCap-ConfigCommonSIB-r17.h"
#include "NR_SIB1-v1700-IEs.h"
#include "NR_UE-NR-Capability.h"
#include "asn_application.h"
#include "constr_TYPE.h"
#include "common/utils/LOG/log.h"
#include "uper_decoder.h"
#include "uper_encoder.h"
#include "openair2/RRC/NR_UE/rrc_ue_redcap.h"
}

namespace {

long *alloc_optional_enum(long value = 0)
{
  auto *field = static_cast<long *>(calloc(1, sizeof(long)));
  EXPECT_NE(field, nullptr);
  if (field != nullptr)
    *field = value;
  return field;
}

NR_SIB1_v1700_IEs_t *make_redcap_sib1(long cell_barred_1rx, long cell_barred_2rx, bool allow_half_duplex)
{
  auto *sib1 = static_cast<NR_SIB1_v1700_IEs_t *>(calloc(1, sizeof(NR_SIB1_v1700_IEs_t)));
  EXPECT_NE(sib1, nullptr);
  if (sib1 == nullptr)
    return nullptr;

  sib1->redCap_ConfigCommon_r17 =
      static_cast<NR_RedCap_ConfigCommonSIB_r17_t *>(calloc(1, sizeof(*sib1->redCap_ConfigCommon_r17)));
  EXPECT_NE(sib1->redCap_ConfigCommon_r17, nullptr);
  if (sib1->redCap_ConfigCommon_r17 == nullptr)
    return sib1;

  if (allow_half_duplex)
    sib1->redCap_ConfigCommon_r17->halfDuplexRedCapAllowed_r17 = alloc_optional_enum();

  sib1->redCap_ConfigCommon_r17->cellBarredRedCap_r17 =
      static_cast<decltype(sib1->redCap_ConfigCommon_r17->cellBarredRedCap_r17)>(
          calloc(1, sizeof(*sib1->redCap_ConfigCommon_r17->cellBarredRedCap_r17)));
  EXPECT_NE(sib1->redCap_ConfigCommon_r17->cellBarredRedCap_r17, nullptr);
  if (sib1->redCap_ConfigCommon_r17->cellBarredRedCap_r17 != nullptr) {
    sib1->redCap_ConfigCommon_r17->cellBarredRedCap_r17->cellBarredRedCap1Rx_r17 = cell_barred_1rx;
    sib1->redCap_ConfigCommon_r17->cellBarredRedCap_r17->cellBarredRedCap2Rx_r17 = cell_barred_2rx;
  }

  sib1->intraFreqReselectionRedCap_r17 =
      alloc_optional_enum(NR_SIB1_v1700_IEs__intraFreqReselectionRedCap_r17_allowed);
  return sib1;
}

} // namespace

TEST(NrRrcRedcap, HalfDuplexOnlyUeRequiresHalfDuplexSib1Flag)
{
  nr_redcap_cfg_t cfg = {};
  cfg.support_of_redcap_r17 = 1;
  cfg.half_duplex_fdd_type_a_redcap_r17 = 1;
  cfg.number_of_rx_redcap_r17 = 1;

  NR_SIB1_v1700_IEs_t sib1 = {};
  sib1.redCap_ConfigCommon_r17 =
      static_cast<NR_RedCap_ConfigCommonSIB_r17_t *>(calloc(1, sizeof(*sib1.redCap_ConfigCommon_r17)));
  ASSERT_NE(sib1.redCap_ConfigCommon_r17, nullptr);

  EXPECT_FALSE(nr_rrc_redcap_sib1_access_allowed(&cfg, &sib1));

  sib1.redCap_ConfigCommon_r17->halfDuplexRedCapAllowed_r17 = alloc_optional_enum();
  EXPECT_TRUE(nr_rrc_redcap_sib1_access_allowed(&cfg, &sib1));

  ASN_STRUCT_FREE_CONTENTS_ONLY(asn_DEF_NR_SIB1_v1700_IEs, &sib1);
}

TEST(NrRrcRedcap, OneRxAndTwoRxBarringFollowSib1Fields)
{
  nr_redcap_cfg_t one_rx_cfg = {};
  one_rx_cfg.support_of_redcap_r17 = 1;
  one_rx_cfg.number_of_rx_redcap_r17 = 1;

  nr_redcap_cfg_t two_rx_cfg = {};
  two_rx_cfg.support_of_redcap_r17 = 1;
  two_rx_cfg.number_of_rx_redcap_r17 = 2;

  NR_SIB1_v1700_IEs_t *sib1 = make_redcap_sib1(
      NR_RedCap_ConfigCommonSIB_r17__cellBarredRedCap_r17__cellBarredRedCap1Rx_r17_barred,
      NR_RedCap_ConfigCommonSIB_r17__cellBarredRedCap_r17__cellBarredRedCap2Rx_r17_notBarred,
      true);
  ASSERT_NE(sib1, nullptr);

  EXPECT_FALSE(nr_rrc_redcap_sib1_access_allowed(&one_rx_cfg, sib1));
  EXPECT_TRUE(nr_rrc_redcap_sib1_access_allowed(&two_rx_cfg, sib1));

  sib1->redCap_ConfigCommon_r17->cellBarredRedCap_r17->cellBarredRedCap1Rx_r17 =
      NR_RedCap_ConfigCommonSIB_r17__cellBarredRedCap_r17__cellBarredRedCap1Rx_r17_notBarred;
  sib1->redCap_ConfigCommon_r17->cellBarredRedCap_r17->cellBarredRedCap2Rx_r17 =
      NR_RedCap_ConfigCommonSIB_r17__cellBarredRedCap_r17__cellBarredRedCap2Rx_r17_barred;

  EXPECT_TRUE(nr_rrc_redcap_sib1_access_allowed(&one_rx_cfg, sib1));
  EXPECT_FALSE(nr_rrc_redcap_sib1_access_allowed(&two_rx_cfg, sib1));

  ASN_STRUCT_FREE(asn_DEF_NR_SIB1_v1700_IEs, sib1);
}

TEST(NrRrcRedcap, SIB1RedCapFieldsEncodeAndDecodeWithoutAsn1Error)
{
  NR_SIB1_v1700_IEs_t *sib1 = make_redcap_sib1(
      NR_RedCap_ConfigCommonSIB_r17__cellBarredRedCap_r17__cellBarredRedCap1Rx_r17_barred,
      NR_RedCap_ConfigCommonSIB_r17__cellBarredRedCap_r17__cellBarredRedCap2Rx_r17_notBarred,
      true);
  ASSERT_NE(sib1, nullptr);

  void *encoded = nullptr;
  const ssize_t encoded_bytes = uper_encode_to_new_buffer(&asn_DEF_NR_SIB1_v1700_IEs, nullptr, sib1, &encoded);
  ASSERT_GT(encoded_bytes, 0);
  ASSERT_NE(encoded, nullptr);

  NR_SIB1_v1700_IEs_t *decoded = nullptr;
  const asn_dec_rval_t dec_rval =
      uper_decode_complete(nullptr, &asn_DEF_NR_SIB1_v1700_IEs, reinterpret_cast<void **>(&decoded), encoded, encoded_bytes);
  ASSERT_EQ(dec_rval.code, RC_OK);
  ASSERT_NE(decoded, nullptr);
  ASSERT_NE(decoded->redCap_ConfigCommon_r17, nullptr);
  ASSERT_NE(decoded->redCap_ConfigCommon_r17->halfDuplexRedCapAllowed_r17, nullptr);
  ASSERT_NE(decoded->redCap_ConfigCommon_r17->cellBarredRedCap_r17, nullptr);
  EXPECT_EQ(decoded->redCap_ConfigCommon_r17->cellBarredRedCap_r17->cellBarredRedCap1Rx_r17,
            NR_RedCap_ConfigCommonSIB_r17__cellBarredRedCap_r17__cellBarredRedCap1Rx_r17_barred);
  EXPECT_EQ(decoded->redCap_ConfigCommon_r17->cellBarredRedCap_r17->cellBarredRedCap2Rx_r17,
            NR_RedCap_ConfigCommonSIB_r17__cellBarredRedCap_r17__cellBarredRedCap2Rx_r17_notBarred);
  ASSERT_NE(decoded->intraFreqReselectionRedCap_r17, nullptr);
  EXPECT_EQ(*decoded->intraFreqReselectionRedCap_r17, NR_SIB1_v1700_IEs__intraFreqReselectionRedCap_r17_allowed);

  free(encoded);
  ASN_STRUCT_FREE(asn_DEF_NR_SIB1_v1700_IEs, decoded);
  ASN_STRUCT_FREE(asn_DEF_NR_SIB1_v1700_IEs, sib1);
}

TEST(NrRrcRedcap, CapabilityBuilderCreatesMinimalRedCapContainerAndRoundTrips)
{
  nr_redcap_cfg_t cfg = {};
  cfg.band = 78;
  cfg.support_of_redcap_r17 = 1;
  cfg.support_of_16drb_redcap_r17 = 1;
  cfg.pdcp_drb_long_sn_redcap_r17 = 1;
  cfg.rlc_am_drb_long_sn_redcap_r17 = 1;

  NR_UE_NR_Capability_t *cap = nr_rrc_build_redcap_ue_capability(&cfg);
  ASSERT_NE(cap, nullptr);
  EXPECT_EQ(cap->accessStratumRelease, NR_AccessStratumRelease_rel17);
  ASSERT_EQ(cap->rf_Parameters.supportedBandListNR.list.count, 1);
  ASSERT_NE(cap->rf_Parameters.supportedBandListNR.list.array[0], nullptr);
  EXPECT_EQ(cap->rf_Parameters.supportedBandListNR.list.array[0]->bandNR, cfg.band);
  ASSERT_NE(cap->pdcp_Parameters.ext2, nullptr);
  ASSERT_NE(cap->pdcp_Parameters.ext2->longSN_RedCap_r17, nullptr);
  ASSERT_NE(cap->rlc_Parameters, nullptr);
  ASSERT_NE(cap->rlc_Parameters->ext2, nullptr);
  ASSERT_NE(cap->rlc_Parameters->ext2->am_WithLongSN_RedCap_r17, nullptr);
  ASSERT_NE(cap->nonCriticalExtension, nullptr);
  ASSERT_NE(cap->nonCriticalExtension->nonCriticalExtension, nullptr);
  ASSERT_NE(cap->nonCriticalExtension->nonCriticalExtension->nonCriticalExtension, nullptr);
  ASSERT_NE(cap->nonCriticalExtension->nonCriticalExtension->nonCriticalExtension->nonCriticalExtension, nullptr);
  ASSERT_NE(cap->nonCriticalExtension->nonCriticalExtension->nonCriticalExtension->nonCriticalExtension->nonCriticalExtension,
            nullptr);
  ASSERT_NE(cap->nonCriticalExtension->nonCriticalExtension->nonCriticalExtension->nonCriticalExtension->nonCriticalExtension
                ->nonCriticalExtension,
            nullptr);
  ASSERT_NE(cap->nonCriticalExtension->nonCriticalExtension->nonCriticalExtension->nonCriticalExtension->nonCriticalExtension
                ->nonCriticalExtension->nonCriticalExtension,
            nullptr);
  ASSERT_NE(cap->nonCriticalExtension->nonCriticalExtension->nonCriticalExtension->nonCriticalExtension->nonCriticalExtension
                ->nonCriticalExtension->nonCriticalExtension->nonCriticalExtension,
            nullptr);
  ASSERT_NE(cap->nonCriticalExtension->nonCriticalExtension->nonCriticalExtension->nonCriticalExtension->nonCriticalExtension
                ->nonCriticalExtension->nonCriticalExtension->nonCriticalExtension->nonCriticalExtension,
            nullptr);
  ASSERT_NE(cap->nonCriticalExtension->nonCriticalExtension->nonCriticalExtension->nonCriticalExtension->nonCriticalExtension
                ->nonCriticalExtension->nonCriticalExtension->nonCriticalExtension->nonCriticalExtension->nonCriticalExtension,
            nullptr);
  ASSERT_NE(cap->nonCriticalExtension->nonCriticalExtension->nonCriticalExtension->nonCriticalExtension->nonCriticalExtension
                ->nonCriticalExtension->nonCriticalExtension->nonCriticalExtension->nonCriticalExtension->nonCriticalExtension
                ->redCapParameters_r17,
            nullptr);
  EXPECT_NE(cap->nonCriticalExtension->nonCriticalExtension->nonCriticalExtension->nonCriticalExtension->nonCriticalExtension
                ->nonCriticalExtension->nonCriticalExtension->nonCriticalExtension->nonCriticalExtension->nonCriticalExtension
                ->redCapParameters_r17->supportOfRedCap_r17,
            nullptr);
  EXPECT_NE(cap->nonCriticalExtension->nonCriticalExtension->nonCriticalExtension->nonCriticalExtension->nonCriticalExtension
                ->nonCriticalExtension->nonCriticalExtension->nonCriticalExtension->nonCriticalExtension->nonCriticalExtension
                ->redCapParameters_r17->supportOf16DRB_RedCap_r17,
            nullptr);

  void *encoded = nullptr;
  const ssize_t encoded_bytes = uper_encode_to_new_buffer(&asn_DEF_NR_UE_NR_Capability, nullptr, cap, &encoded);
  ASSERT_GT(encoded_bytes, 0);
  ASSERT_NE(encoded, nullptr);

  NR_UE_NR_Capability_t *decoded = nullptr;
  const asn_dec_rval_t dec_rval =
      uper_decode_complete(nullptr, &asn_DEF_NR_UE_NR_Capability, reinterpret_cast<void **>(&decoded), encoded, encoded_bytes);
  ASSERT_EQ(dec_rval.code, RC_OK);
  ASSERT_NE(decoded, nullptr);
  ASSERT_EQ(decoded->rf_Parameters.supportedBandListNR.list.count, 1);
  EXPECT_EQ(decoded->rf_Parameters.supportedBandListNR.list.array[0]->bandNR, cfg.band);

  free(encoded);
  ASN_STRUCT_FREE(asn_DEF_NR_UE_NR_Capability, decoded);
  ASN_STRUCT_FREE(asn_DEF_NR_UE_NR_Capability, cap);
}

int main(int argc, char **argv)
{
  logInit();
  set_log(NR_RRC, OAILOG_DEBUG);
  testing::InitGoogleTest(&argc, argv);
  return RUN_ALL_TESTS();
}
