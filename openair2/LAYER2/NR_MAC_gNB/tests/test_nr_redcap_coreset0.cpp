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

#include <gtest/gtest.h>

extern "C" {
#include "openair2/LAYER2/NR_MAC_gNB/nr_mac_redcap.h"
}

TEST(nr_redcap_coreset0, valid_modes)
{
  EXPECT_TRUE(nr_redcap_is_valid_coreset0_mode(NR_REDCAP_CORESET0_MODE_CASE_A));
  EXPECT_TRUE(nr_redcap_is_valid_coreset0_mode(NR_REDCAP_CORESET0_MODE_CASE_B));
  EXPECT_FALSE(nr_redcap_is_valid_coreset0_mode(-1));
  EXPECT_FALSE(nr_redcap_is_valid_coreset0_mode(2));
}

TEST(nr_redcap_coreset0, mode_to_string)
{
  EXPECT_STREQ("case-a-full-cell", nr_redcap_coreset0_mode_to_string(NR_REDCAP_CORESET0_MODE_CASE_A));
  EXPECT_STREQ("case-b-edge-only", nr_redcap_coreset0_mode_to_string(NR_REDCAP_CORESET0_MODE_CASE_B));
}

TEST(nr_redcap_coreset0, edge_alignment_accepts_lower_edge)
{
  EXPECT_TRUE(nr_redcap_is_edge_aligned_bwp(0, 51, 106));
}

TEST(nr_redcap_coreset0, edge_alignment_accepts_upper_edge)
{
  EXPECT_TRUE(nr_redcap_is_edge_aligned_bwp(55, 51, 106));
}

TEST(nr_redcap_coreset0, edge_alignment_rejects_internal_bwp)
{
  EXPECT_FALSE(nr_redcap_is_edge_aligned_bwp(10, 51, 106));
}

TEST(nr_redcap_coreset0, edge_alignment_rejects_invalid_ranges)
{
  EXPECT_FALSE(nr_redcap_is_edge_aligned_bwp(-1, 51, 106));
  EXPECT_FALSE(nr_redcap_is_edge_aligned_bwp(60, 51, 106));
  EXPECT_FALSE(nr_redcap_is_edge_aligned_bwp(0, 0, 106));
}

int main(int argc, char **argv)
{
  testing::InitGoogleTest(&argc, argv);
  return RUN_ALL_TESTS();
}
