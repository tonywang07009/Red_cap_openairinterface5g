#include "rrc_ue_redcap.h"

#include "common/utils/LOG/log.h"
#include "common/utils/oai_asn1.h"
#include "common/utils/utils.h"

static void set_optional_enum_supported(long **field)
{
  *field = CALLOC(1, sizeof(**field));
  **field = 0;
}

NR_UE_NR_Capability_t *nr_rrc_build_redcap_ue_capability(const nr_redcap_cfg_t *cfg)
{
  AssertFatal(cfg != NULL, "cfg must not be NULL\n");

  NR_UE_NR_Capability_t *cap = calloc_or_fail(1, sizeof(*cap));
  cap->accessStratumRelease = NR_AccessStratumRelease_rel17;
  cap->pdcp_Parameters.maxNumberROHC_ContextSessions = NR_PDCP_Parameters__maxNumberROHC_ContextSessions_cs2;

  asn1cSequenceAdd(cap->rf_Parameters.supportedBandListNR.list, NR_BandNR_t, band);
  band->bandNR = cfg->band;
  if (cfg->pusch_256qam) {
    band->pusch_256QAM = calloc_or_fail(1, sizeof(*band->pusch_256QAM));
    *band->pusch_256QAM = NR_BandNR__pusch_256QAM_supported;
  }
  if (cfg->pdsch_256qam) {
    cap->phy_Parameters.phy_ParametersFR1 = calloc_or_fail(1, sizeof(*cap->phy_Parameters.phy_ParametersFR1));
    cap->phy_Parameters.phy_ParametersFR1->pdsch_256QAM_FR1 =
        calloc_or_fail(1, sizeof(*cap->phy_Parameters.phy_ParametersFR1->pdsch_256QAM_FR1));
    *cap->phy_Parameters.phy_ParametersFR1->pdsch_256QAM_FR1 = NR_Phy_ParametersFR1__pdsch_256QAM_FR1_supported;
  }

  if (cfg->pdcp_drb_long_sn_redcap_r17) {
    asn1cCalloc(cap->pdcp_Parameters.ext2, ext2);
    set_optional_enum_supported(&ext2->longSN_RedCap_r17);
  }

  if (cfg->rlc_am_drb_long_sn_redcap_r17) {
    cap->rlc_Parameters = calloc_or_fail(1, sizeof(*cap->rlc_Parameters));
    asn1cCalloc(cap->rlc_Parameters->ext2, ext2);
    set_optional_enum_supported(&ext2->am_WithLongSN_RedCap_r17);
  }

  asn1cCalloc(cap->nonCriticalExtension, v1530);
  asn1cCalloc(v1530->nonCriticalExtension, v1540);
  asn1cCalloc(v1540->nonCriticalExtension, v1550);
  asn1cCalloc(v1550->nonCriticalExtension, v1560);
  asn1cCalloc(v1560->nonCriticalExtension, v1570);
  asn1cCalloc(v1570->nonCriticalExtension, v1610);
  asn1cCalloc(v1610->nonCriticalExtension, v1640);
  asn1cCalloc(v1640->nonCriticalExtension, v1650);
  asn1cCalloc(v1650->nonCriticalExtension, v1690);
  asn1cCalloc(v1690->nonCriticalExtension, v1700);
  asn1cCalloc(v1700->redCapParameters_r17, redcap);

  if (cfg->support_of_redcap_r17)
    set_optional_enum_supported(&redcap->supportOfRedCap_r17);
  if (cfg->support_of_16drb_redcap_r17)
    set_optional_enum_supported(&redcap->supportOf16DRB_RedCap_r17);

  return cap;
}

const NR_RedCap_ConfigCommonSIB_r17_t *nr_rrc_parse_redcap_sib1(const NR_SIB1_v1700_IEs_t *sib1_v1700)
{
  if (sib1_v1700 == NULL)
    return NULL;

  return sib1_v1700->redCap_ConfigCommon_r17;
}

bool nr_rrc_redcap_sib1_access_allowed(const nr_redcap_cfg_t *cfg, const NR_SIB1_v1700_IEs_t *sib1_v1700)
{
  if (cfg == NULL || !cfg->support_of_redcap_r17)
    return true;

  const NR_RedCap_ConfigCommonSIB_r17_t *redcap_sib = nr_rrc_parse_redcap_sib1(sib1_v1700);
  if (redcap_sib == NULL)
    return true;

  if (cfg->half_duplex_fdd_type_a_redcap_r17 && redcap_sib->halfDuplexRedCapAllowed_r17 == NULL) {
    LOG_W(NR_RRC,
          "RedCap UE is configured as half-duplex FDD Type A, but SIB1 omits halfDuplexRedCapAllowed-r17: treating cell as barred\n");
    return false;
  }

  if (redcap_sib->cellBarredRedCap_r17 == NULL)
    return true;

  if (cfg->number_of_rx_redcap_r17 == 1
      && redcap_sib->cellBarredRedCap_r17->cellBarredRedCap1Rx_r17
             == NR_RedCap_ConfigCommonSIB_r17__cellBarredRedCap_r17__cellBarredRedCap1Rx_r17_barred) {
    LOG_W(NR_RRC, "SIB1 bars 1Rx RedCap UEs on this cell\n");
    return false;
  }

  if (cfg->number_of_rx_redcap_r17 == 2
      && redcap_sib->cellBarredRedCap_r17->cellBarredRedCap2Rx_r17
             == NR_RedCap_ConfigCommonSIB_r17__cellBarredRedCap_r17__cellBarredRedCap2Rx_r17_barred) {
    LOG_W(NR_RRC, "SIB1 bars 2Rx RedCap UEs on this cell\n");
    return false;
  }

  return true;
}
