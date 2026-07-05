/*
 * Licensed to the OpenAirInterface (OAI) Software Alliance under one or more
 * contributor license agreements.  See the NOTICE file distributed with
 * this work for additional information regarding copyright ownership.
 * The OpenAirInterface Software Alliance licenses this file to You under
 * the OAI Public License, Version 1.1  (the "License"); you may not use this file
 * except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.openairinterface.org/?page_id=698
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *-------------------------------------------------------------------------------
 * For more information about the OpenAirInterface (OAI) Software Alliance:
 *      contact@openairinterface.org
 */

#include "gtest/gtest.h"
extern "C" {
#include <stdlib.h>
#include "openair1/PHY/defs_nr_common.h"
#include "openair1/PHY/INIT/nr_phy_init.h"
#include "openair3/UICC/usim_interface.h"

static softmodem_params_t softmodem_params;
softmodem_params_t *get_softmodem_params(void)
{
  return &softmodem_params;
}

bool load_nr_redcap_config(const char *sectionName, nr_redcap_cfg_t *cfg)
{
  (void)sectionName;
  if (cfg != NULL)
    *cfg = (nr_redcap_cfg_t){0};
  return false;
}
}

uint32_t ref_get_samples_slot_timestamp(NR_DL_FRAME_PARMS *fp, unsigned int slot)
{
  uint32_t samp_count = 0;
  for (unsigned int i = 0; i < slot; i++) {
    samp_count += get_samples_per_slot(i, fp);
  }
  return samp_count;
}

uint32_t ref_get_slot_from_timestamp(openair0_timestamp ts, NR_DL_FRAME_PARMS *fp)
{
  uint32_t slot_idx = 0;
  int samples_till_the_slot = get_samples_per_slot(slot_idx, fp) - 1;
  ts = ts % fp->samples_per_frame;

  while (ts > samples_till_the_slot) {
    slot_idx++;
    samples_till_the_slot += get_samples_per_slot(slot_idx, fp);
  }
  return slot_idx;
}

static NR_DL_FRAME_PARMS make_redcap_fp(uint8_t mu)
{
  NR_DL_FRAME_PARMS fp;
  memset(&fp, 0, sizeof(fp));
  fp.numerology_index = mu;
  fp.freq_range = FR1;
  fp.nr_band = 78;
  fp.dl_CarrierFreq = 3600000000;
  fp.ul_CarrierFreq = 3510000000;
  fp.N_RB_DL = (mu == NR_MU_0) ? 106 : 51;
  fp.N_RB_UL = fp.N_RB_DL;
  fp.nb_antennas_rx = 2;
  fp.nb_antennas_tx = 1;
  return fp;
}

void test_coherence_symbol_api(NR_DL_FRAME_PARMS *fp)
{
  EXPECT_EQ(get_samples_symbol_timestamp(fp, 0, 0), get_samples_slot_timestamp(fp, 0));

  for (int slot = 0; slot < 4; slot++) {
    EXPECT_EQ(get_samples_symbol_duration(fp, slot, 0, fp->symbols_per_slot) + get_samples_slot_timestamp(fp, slot),
              get_samples_slot_timestamp(fp, slot + 1));
  }

  for (int symbol = 0; symbol < fp->symbols_per_slot - 1; symbol++) {
    EXPECT_EQ(get_samples_symbol_timestamp(fp, 0, symbol + 1) - get_samples_symbol_timestamp(fp, 0, symbol),
              get_samples_symbol_duration(fp, 0, symbol, 1));
  }
}

void test_coherence_slot_api(NR_DL_FRAME_PARMS *fp)
{
  for (unsigned int slot = 0; slot < fp->slots_per_frame; slot++) {
    EXPECT_EQ(get_samples_slot_timestamp(fp, slot), ref_get_samples_slot_timestamp(fp, slot));
  }

  openair0_timestamp ts = get_samples_per_slot(0, fp);
  // When timestamp is the last sample of the slot
  EXPECT_EQ(get_slot_from_timestamp(ts - 1, fp), 0);
  for (unsigned int slot = 0; slot < fp->slots_per_frame; slot++) {
    // When timestamp is the first sample of the slot
    ts = ref_get_samples_slot_timestamp(fp, slot);
    EXPECT_EQ(get_slot_from_timestamp(ts, fp), slot);
    // When timestamp is anywhere in the slot
    ts += (rand() % fp->samples_per_slotN0);
    EXPECT_EQ(get_slot_from_timestamp(ts, fp), slot);
  }
}

TEST(nr_frame_params, test_mu_3)
{
  NR_DL_FRAME_PARMS fp;
  int mu = NR_MU_3;
  memset(&fp, 0, sizeof(fp));
  nfapi_nr_config_request_scf_t cfg;
  cfg.carrier_config.num_rx_ant.value = 4;
  cfg.carrier_config.num_tx_ant.value = 4;
  cfg.carrier_config.dl_grid_size[mu].value = 66;
  cfg.carrier_config.ul_grid_size[mu].value = 66;
  cfg.cell_config.frame_duplex_type.value = TDD;
  cfg.ssb_config.scs_common.value = mu;
  fp.dl_CarrierFreq = 27524520000;
  fp.nr_band = 261;
  nr_init_frame_parms(&cfg, &fp);
  nr_dump_frame_parms(&fp);
  test_coherence_symbol_api(&fp);
  test_coherence_slot_api(&fp);
}

TEST(nr_frame_params, test_mu_2)
{
  NR_DL_FRAME_PARMS fp;
  int mu = NR_MU_2;
  memset(&fp, 0, sizeof(fp));
  nfapi_nr_config_request_scf_t cfg;
  cfg.carrier_config.num_rx_ant.value = 4;
  cfg.carrier_config.num_tx_ant.value = 4;
  cfg.carrier_config.dl_grid_size[mu].value = 51;
  cfg.carrier_config.ul_grid_size[mu].value = 51;
  cfg.cell_config.frame_duplex_type.value = TDD;
  cfg.ssb_config.scs_common.value = mu;
  fp.dl_CarrierFreq = 27524520000;
  fp.nr_band = 261;
  nr_init_frame_parms(&cfg, &fp);
  nr_dump_frame_parms(&fp);
  test_coherence_symbol_api(&fp);
  test_coherence_slot_api(&fp);
}

TEST(nr_frame_params, test_mu_1)
{
  NR_DL_FRAME_PARMS fp;
  int mu = NR_MU_1;
  memset(&fp, 0, sizeof(fp));
  nfapi_nr_config_request_scf_t cfg;
  cfg.carrier_config.num_rx_ant.value = 4;
  cfg.carrier_config.num_tx_ant.value = 4;
  cfg.carrier_config.dl_grid_size[mu].value = 106;
  cfg.carrier_config.ul_grid_size[mu].value = 106;
  cfg.cell_config.frame_duplex_type.value = TDD;
  cfg.ssb_config.scs_common.value = mu;
  fp.dl_CarrierFreq = 3600000000;
  fp.nr_band = 78;
  nr_init_frame_parms(&cfg, &fp);
  nr_dump_frame_parms(&fp);
  test_coherence_symbol_api(&fp);
  test_coherence_slot_api(&fp);
}

TEST(nr_frame_params, test_mu_0)
{
  int mu = NR_MU_0;
  NR_DL_FRAME_PARMS fp;
  memset(&fp, 0, sizeof(fp));
  nfapi_nr_config_request_scf_t cfg;
  cfg.carrier_config.num_rx_ant.value = 4;
  cfg.carrier_config.num_tx_ant.value = 4;
  cfg.carrier_config.dl_grid_size[mu].value = 216;
  cfg.carrier_config.ul_grid_size[mu].value = 216;
  cfg.cell_config.frame_duplex_type.value = TDD;
  cfg.ssb_config.scs_common.value = mu;
  fp.dl_CarrierFreq = 2600000000;
  fp.nr_band = 38;
  nr_init_frame_parms(&cfg, &fp);
  nr_dump_frame_parms(&fp);
  test_coherence_symbol_api(&fp);
  test_coherence_slot_api(&fp);
}

TEST(nr_frame_params, redcap_gnb_validation_accepts_fr1_limits)
{
  NR_DL_FRAME_PARMS fp = make_redcap_fp(NR_MU_1);
  fp.nb_antennas_tx = 2;

  nr_validate_redcap_gnb_frame_parms(&fp);
}

TEST(nr_frame_params, redcap_gnb_validation_allows_common_grid_over_20mhz)
{
  NR_DL_FRAME_PARMS fp = make_redcap_fp(NR_MU_1);
  fp.nb_antennas_tx = 2;
  fp.N_RB_DL = 52;

  nr_validate_redcap_gnb_frame_parms(&fp);
}

TEST(nr_frame_params, redcap_ue_validation_rejects_dl_bandwidth_over_20mhz)
{
  NR_DL_FRAME_PARMS fp = make_redcap_fp(NR_MU_1);
  fp.N_RB_DL = 52;

  ASSERT_DEATH({ nr_validate_redcap_ue_frame_parms(&fp); }, "exceeds 20 MHz limit");
}

TEST(nr_frame_params, redcap_ue_validation_rejects_extra_rx_branch)
{
  NR_DL_FRAME_PARMS fp = make_redcap_fp(NR_MU_0);
  fp.nb_antennas_rx = 3;

  ASSERT_DEATH({ nr_validate_redcap_ue_frame_parms(&fp); }, "requires 1 or 2 RX branches");
}

TEST(nr_frame_params, redcap_ue_validation_rejects_ul_mimo)
{
  NR_DL_FRAME_PARMS fp = make_redcap_fp(NR_MU_0);
  fp.nb_antennas_tx = 2;

  ASSERT_DEATH({ nr_validate_redcap_ue_frame_parms(&fp); }, "does not support UL MIMO");
}

int main(int argc, char **argv)
{
  uniqCfg = load_configmodule(argc, argv, CONFIG_ENABLECMDLINEONLY);
  logInit();
  testing::InitGoogleTest(&argc, argv);
  return RUN_ALL_TESTS();
}
