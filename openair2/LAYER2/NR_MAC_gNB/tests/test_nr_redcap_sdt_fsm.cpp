#include <array>
#include <cstdio>
#include <gtest/gtest.h>

#include <sstream>
#include <string>
#include <vector>

extern "C" {
#include "../nr_mac_sdt_fsm.h"
}

static std::string join_states(const std::vector<nr_redcap_sdt_state_t> &states)
{
  std::ostringstream oss;
  for (size_t i = 0; i < states.size(); ++i) {
    if (i > 0)
      oss << " -> ";
    oss << nr_redcap_sdt_state_to_string(states[i]);
  }
  return oss.str();
}

static std::string read_file(FILE *stream)
{
  std::array<char, 256> buffer = {};
  std::string text;
  rewind(stream);
  while (fgets(buffer.data(), buffer.size(), stream) != nullptr)
    text += buffer.data();
  return text;
}

TEST(NrRedcapSdtFsm, UsesMsgAPathForSmallPayloadAndEndsInactive)
{
  nr_redcap_sdt_fsm_t fsm = {};
  nr_redcap_sdt_transition_t transition = {};
  nr_redcap_sdt_fsm_init(&fsm, true, NR_REDCAP_SDT_MSGA_PAYLOAD_THRESHOLD_BYTES);

  std::vector<nr_redcap_sdt_state_t> states = {fsm.state};
  EXPECT_EQ(fsm.redcap_rrc_state, NR_REDCAP_RRC_IDLE);

  ASSERT_TRUE(nr_redcap_sdt_fsm_step(&fsm, NR_REDCAP_SDT_EVENT_UL_DATA_ARRIVAL, 128, &transition));
  states.push_back(fsm.state);
  EXPECT_EQ(transition.from, NR_REDCAP_SDT_STATE_IDLE);
  EXPECT_EQ(transition.to, NR_REDCAP_SDT_STATE_TRIGGER);
  EXPECT_EQ(fsm.redcap_rrc_state, NR_REDCAP_RRC_CONNECTED);

  ASSERT_TRUE(nr_redcap_sdt_fsm_step(&fsm, NR_REDCAP_SDT_EVENT_SELECT_PATH, 0, &transition));
  states.push_back(fsm.state);
  EXPECT_EQ(fsm.selected_path, NR_REDCAP_SDT_PATH_MSGA);
  EXPECT_STREQ(nr_redcap_sdt_path_to_string(fsm.selected_path), "msga");

  ASSERT_TRUE(nr_redcap_sdt_fsm_step(&fsm, NR_REDCAP_SDT_EVENT_UL_GRANT_READY, 0, &transition));
  states.push_back(fsm.state);

  ASSERT_TRUE(nr_redcap_sdt_fsm_step(&fsm, NR_REDCAP_SDT_EVENT_UL_BURST_COMPLETE, 0, &transition));
  states.push_back(fsm.state);
  EXPECT_EQ(fsm.redcap_rrc_state, NR_REDCAP_RRC_INACTIVE);
  EXPECT_EQ(join_states(states), "idle -> sdt-trigger -> msga-path -> sdt-active -> inactive");
}

TEST(NrRedcapSdtFsm, FallsBackToMsg3ForLargePayload)
{
  nr_redcap_sdt_fsm_t fsm = {};
  nr_redcap_sdt_transition_t transition = {};
  nr_redcap_sdt_fsm_init(&fsm, true, NR_REDCAP_SDT_MSGA_PAYLOAD_THRESHOLD_BYTES);

  ASSERT_TRUE(nr_redcap_sdt_fsm_step(&fsm, NR_REDCAP_SDT_EVENT_UL_DATA_ARRIVAL, NR_REDCAP_SDT_MSGA_PAYLOAD_THRESHOLD_BYTES, &transition));
  ASSERT_TRUE(nr_redcap_sdt_fsm_step(&fsm, NR_REDCAP_SDT_EVENT_SELECT_PATH, 0, &transition));
  EXPECT_EQ(fsm.selected_path, NR_REDCAP_SDT_PATH_MSG3);
  EXPECT_EQ(fsm.state, NR_REDCAP_SDT_STATE_MSG3_PATH);
  EXPECT_STREQ(nr_redcap_sdt_state_to_string(fsm.state), "msg3-path");

  ASSERT_TRUE(nr_redcap_sdt_fsm_step(&fsm, NR_REDCAP_SDT_EVENT_UL_GRANT_READY, 0, &transition));
  ASSERT_TRUE(nr_redcap_sdt_fsm_step(&fsm, NR_REDCAP_SDT_EVENT_UL_BURST_COMPLETE, 0, &transition));
  EXPECT_EQ(fsm.state, NR_REDCAP_SDT_STATE_INACTIVE);
}

TEST(NrRedcapSdtFsm, ReturnsToIdleWhenInactiveIsDisabled)
{
  nr_redcap_sdt_fsm_t fsm = {};
  nr_redcap_sdt_transition_t transition = {};
  nr_redcap_sdt_fsm_init(&fsm, false, NR_REDCAP_SDT_MSGA_PAYLOAD_THRESHOLD_BYTES);

  ASSERT_TRUE(nr_redcap_sdt_fsm_step(&fsm, NR_REDCAP_SDT_EVENT_UL_DATA_ARRIVAL, 32, &transition));
  ASSERT_TRUE(nr_redcap_sdt_fsm_step(&fsm, NR_REDCAP_SDT_EVENT_SELECT_PATH, 0, &transition));
  ASSERT_TRUE(nr_redcap_sdt_fsm_step(&fsm, NR_REDCAP_SDT_EVENT_UL_GRANT_READY, 0, &transition));
  ASSERT_TRUE(nr_redcap_sdt_fsm_step(&fsm, NR_REDCAP_SDT_EVENT_UL_BURST_COMPLETE, 0, &transition));

  EXPECT_EQ(fsm.state, NR_REDCAP_SDT_STATE_IDLE);
  EXPECT_EQ(fsm.redcap_rrc_state, NR_REDCAP_RRC_IDLE);
  EXPECT_FALSE(nr_redcap_sdt_fsm_step(&fsm, NR_REDCAP_SDT_EVENT_SELECT_PATH, 0, &transition));
}

TEST(NrRedcapSdtFsm, WritesTransitionLogForVerification)
{
  nr_redcap_sdt_fsm_t fsm = {};
  nr_redcap_sdt_transition_t transition = {};
  nr_redcap_sdt_fsm_init(&fsm, true, NR_REDCAP_SDT_MSGA_PAYLOAD_THRESHOLD_BYTES);

  FILE *transition_log = tmpfile();
  ASSERT_NE(transition_log, nullptr);

  ASSERT_TRUE(nr_redcap_sdt_fsm_step(&fsm, NR_REDCAP_SDT_EVENT_UL_DATA_ARRIVAL, 128, &transition));
  ASSERT_GT(nr_redcap_sdt_transition_fprintf(transition_log, &transition), 0);
  ASSERT_TRUE(nr_redcap_sdt_fsm_step(&fsm, NR_REDCAP_SDT_EVENT_SELECT_PATH, 0, &transition));
  ASSERT_GT(nr_redcap_sdt_transition_fprintf(transition_log, &transition), 0);
  ASSERT_TRUE(nr_redcap_sdt_fsm_step(&fsm, NR_REDCAP_SDT_EVENT_UL_GRANT_READY, 0, &transition));
  ASSERT_GT(nr_redcap_sdt_transition_fprintf(transition_log, &transition), 0);
  ASSERT_TRUE(nr_redcap_sdt_fsm_step(&fsm, NR_REDCAP_SDT_EVENT_UL_BURST_COMPLETE, 0, &transition));
  ASSERT_GT(nr_redcap_sdt_transition_fprintf(transition_log, &transition), 0);

  const std::string expected =
      "event=ul-data-arrival accepted=true from=idle to=sdt-trigger path=none rrc=connected pending_payload_bytes=128\n"
      "event=select-path accepted=true from=sdt-trigger to=msga-path path=msga rrc=connected pending_payload_bytes=128\n"
      "event=ul-grant-ready accepted=true from=msga-path to=sdt-active path=msga rrc=connected pending_payload_bytes=128\n"
      "event=ul-burst-complete accepted=true from=sdt-active to=inactive path=msga rrc=inactive pending_payload_bytes=0\n";
  EXPECT_EQ(read_file(transition_log), expected);

  fclose(transition_log);
}

TEST(NrRedcapSdtFsm, StartUlBurstExpandsSchedulerSequence)
{
  nr_redcap_sdt_fsm_t fsm = {};
  nr_redcap_sdt_transition_t transitions[3] = {};
  nr_redcap_sdt_fsm_init(&fsm, true, NR_REDCAP_SDT_MSGA_PAYLOAD_THRESHOLD_BYTES);

  const size_t expected_transitions = sizeof(transitions) / sizeof(transitions[0]);
  const size_t num_transitions = nr_redcap_sdt_start_ul_burst(&fsm, 128, transitions, expected_transitions);

  ASSERT_EQ(num_transitions, expected_transitions);
  EXPECT_EQ(transitions[0].event, NR_REDCAP_SDT_EVENT_UL_DATA_ARRIVAL);
  EXPECT_EQ(transitions[1].event, NR_REDCAP_SDT_EVENT_SELECT_PATH);
  EXPECT_EQ(transitions[2].event, NR_REDCAP_SDT_EVENT_UL_GRANT_READY);
  EXPECT_EQ(fsm.state, NR_REDCAP_SDT_STATE_ACTIVE);
  EXPECT_EQ(fsm.selected_path, NR_REDCAP_SDT_PATH_MSGA);
}

TEST(NrRedcapSdtFsm, CompleteUlBurstWaitsForEmptySchedulerView)
{
  nr_redcap_sdt_fsm_t fsm = {};
  nr_redcap_sdt_transition_t transition = {};
  nr_redcap_sdt_transition_t transitions[3] = {};
  nr_redcap_sdt_fsm_init(&fsm, true, NR_REDCAP_SDT_MSGA_PAYLOAD_THRESHOLD_BYTES);

  ASSERT_EQ(3U, nr_redcap_sdt_start_ul_burst(&fsm, 320, transitions, sizeof(transitions) / sizeof(transitions[0])));
  EXPECT_EQ(fsm.state, NR_REDCAP_SDT_STATE_ACTIVE);
  EXPECT_EQ(fsm.selected_path, NR_REDCAP_SDT_PATH_MSG3);

  EXPECT_FALSE(nr_redcap_sdt_complete_ul_burst(&fsm, true, &transition));
  EXPECT_EQ(fsm.state, NR_REDCAP_SDT_STATE_ACTIVE);

  ASSERT_TRUE(nr_redcap_sdt_complete_ul_burst(&fsm, false, &transition));
  EXPECT_EQ(transition.event, NR_REDCAP_SDT_EVENT_UL_BURST_COMPLETE);
  EXPECT_EQ(fsm.state, NR_REDCAP_SDT_STATE_INACTIVE);
}

int main(int argc, char **argv)
{
  testing::InitGoogleTest(&argc, argv);
  return RUN_ALL_TESTS();
}
