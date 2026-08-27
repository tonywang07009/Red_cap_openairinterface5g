#include "ran_func_kpm.h"

#include "common/ran_context.h"
#include "openair2/RRC/NR/nr_rrc_defs.h"

#include <assert.h>
#include <stdbool.h>
#include <string.h>

RAN_CONTEXT_t RC;

static bool name_is(const byte_array_t name, const char *expected)
{
  const size_t len = strlen(expected);
  return name.len == len && memcmp(name.buf, expected, len) == 0;
}

static const ric_report_style_item_t *find_report_style(const kpm_e2_setup_t *setup, const ric_service_report_e type)
{
  for (size_t i = 0; i < setup->ran_func_def.sz_ric_report_style_list; ++i) {
    const ric_report_style_item_t *style = &setup->ran_func_def.ric_report_style_list[i];
    if (style->report_style_type == type)
      return style;
  }
  return NULL;
}

static void assert_cell_and_ue_styles(const ngran_node_t node_type)
{
  gNB_RRC_INST rrc = {.node_type = node_type};
  gNB_RRC_INST *rrc_instances[] = {&rrc};
  RC.nrrrc = rrc_instances;

  kpm_e2_setup_t setup = {0};
  read_kpm_setup_sm(&setup);

  assert(setup.ran_func_def.sz_ric_report_style_list == 2);

  const ric_report_style_item_t *cell = find_report_style(&setup, STYLE_1_RIC_SERVICE_REPORT);
  assert(cell != NULL);
  assert(cell->act_def_format_type == FORMAT_1_ACTION_DEFINITION);
  assert(cell->ind_hdr_format_type == FORMAT_1_INDICATION_HEADER);
  assert(cell->ind_msg_format_type == FORMAT_1_INDICATION_MESSAGE);
  assert(cell->meas_info_for_action_lst_len == 2);
  assert(name_is(cell->meas_info_for_action_lst[0].name, "RRU.PrbTotDl"));
  assert(name_is(cell->meas_info_for_action_lst[1].name, "RRU.PrbTotUl"));

  const ric_report_style_item_t *ue = find_report_style(&setup, STYLE_4_RIC_SERVICE_REPORT);
  assert(ue != NULL);
  assert(ue->act_def_format_type == FORMAT_4_ACTION_DEFINITION);
  assert(ue->ind_hdr_format_type == FORMAT_1_INDICATION_HEADER);
  assert(ue->ind_msg_format_type == FORMAT_3_INDICATION_MESSAGE);

  free_kpm_ran_function_def(&setup.ran_func_def);
}

static void assert_cuup_does_not_advertise_cell_style(void)
{
  gNB_RRC_INST rrc = {.node_type = ngran_gNB_CUUP};
  gNB_RRC_INST *rrc_instances[] = {&rrc};
  RC.nrrrc = rrc_instances;

  kpm_e2_setup_t setup = {0};
  read_kpm_setup_sm(&setup);

  assert(setup.ran_func_def.sz_ric_report_style_list == 1);
  assert(find_report_style(&setup, STYLE_1_RIC_SERVICE_REPORT) == NULL);
  assert(find_report_style(&setup, STYLE_4_RIC_SERVICE_REPORT) != NULL);

  free_kpm_ran_function_def(&setup.ran_func_def);
}

int main(void)
{
  assert_cell_and_ue_styles(ngran_gNB);
  assert_cell_and_ue_styles(ngran_gNB_DU);
  assert_cuup_does_not_advertise_cell_style();
  return 0;
}
