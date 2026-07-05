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

#include <cstdlib>
#include <gtest/gtest.h>

extern "C" {
#include "openair2/E2AP/RAN_FUNCTION/O-RAN/ran_func_rc_redcap.h"
#include "openair2/E2AP/flexric/src/sm/rc_sm/ie/ir/ran_parameter_value.h"
}

static seq_ran_param_t make_integer_param(const uint32_t ran_param_id, const int64_t value)
{
  seq_ran_param_t ran_param = {};
  ran_param.ran_param_id = ran_param_id;
  ran_param.ran_param_val.type = ELEMENT_KEY_FLAG_TRUE_RAN_PARAMETER_VAL_TYPE;
  ran_param.ran_param_val.flag_true = static_cast<ran_parameter_value_t *>(calloc(1, sizeof(ran_parameter_value_t)));
  EXPECT_NE(nullptr, ran_param.ran_param_val.flag_true);
  ran_param.ran_param_val.flag_true->type = INTEGER_RAN_PARAMETER_VALUE;
  ran_param.ran_param_val.flag_true->int_ran = value;
  return ran_param;
}

static void free_ctrl_msg(e2sm_rc_ctrl_msg_frmt_1_t *msg)
{
  if (msg == nullptr || msg->ran_param == nullptr)
    return;

  for (size_t i = 0; i < msg->sz_ran_param; ++i)
    free(msg->ran_param[i].ran_param_val.flag_true);

  free(msg->ran_param);
  msg->ran_param = nullptr;
  msg->sz_ran_param = 0;
}

TEST(nr_redcap_rc_ctrl, parses_valid_ul_prb_message)
{
  e2sm_rc_ctrl_msg_frmt_1_t msg = {};
  msg.sz_ran_param = 2;
  msg.ran_param = static_cast<seq_ran_param_t *>(calloc(msg.sz_ran_param, sizeof(seq_ran_param_t)));
  ASSERT_NE(nullptr, msg.ran_param);
  msg.ran_param[0] = make_integer_param(NR_REDCAP_RC_RAN_PARAM_ID_MAX_UL_PRB, 6);
  msg.ran_param[1] = make_integer_param(NR_REDCAP_RC_RAN_PARAM_ID_UE_RNTI, 0x4601);

  nr_redcap_rc_ul_prb_ctrl_t ctrl = {};
  EXPECT_TRUE(nr_redcap_parse_ul_prb_ctrl_message(&msg, &ctrl));
  EXPECT_EQ(0x4601, ctrl.rnti);
  EXPECT_EQ(6, ctrl.max_ul_prbs);

  free_ctrl_msg(&msg);
}

TEST(nr_redcap_rc_ctrl, rejects_missing_rnti_param)
{
  e2sm_rc_ctrl_msg_frmt_1_t msg = {};
  msg.sz_ran_param = 1;
  msg.ran_param = static_cast<seq_ran_param_t *>(calloc(msg.sz_ran_param, sizeof(seq_ran_param_t)));
  ASSERT_NE(nullptr, msg.ran_param);
  msg.ran_param[0] = make_integer_param(NR_REDCAP_RC_RAN_PARAM_ID_MAX_UL_PRB, 8);

  nr_redcap_rc_ul_prb_ctrl_t ctrl = {};
  EXPECT_FALSE(nr_redcap_parse_ul_prb_ctrl_message(&msg, &ctrl));

  free_ctrl_msg(&msg);
}

TEST(nr_redcap_rc_ctrl, rejects_out_of_range_rnti)
{
  e2sm_rc_ctrl_msg_frmt_1_t msg = {};
  msg.sz_ran_param = 2;
  msg.ran_param = static_cast<seq_ran_param_t *>(calloc(msg.sz_ran_param, sizeof(seq_ran_param_t)));
  ASSERT_NE(nullptr, msg.ran_param);
  msg.ran_param[0] = make_integer_param(NR_REDCAP_RC_RAN_PARAM_ID_UE_RNTI, 70000);
  msg.ran_param[1] = make_integer_param(NR_REDCAP_RC_RAN_PARAM_ID_MAX_UL_PRB, 8);

  nr_redcap_rc_ul_prb_ctrl_t ctrl = {};
  EXPECT_FALSE(nr_redcap_parse_ul_prb_ctrl_message(&msg, &ctrl));

  free_ctrl_msg(&msg);
}

int main(int argc, char **argv)
{
  testing::InitGoogleTest(&argc, argv);
  return RUN_ALL_TESTS();
}
