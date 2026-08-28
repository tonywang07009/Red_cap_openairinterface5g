#include "ran_func_kpm.h"

#include "common/ran_context.h"
#include "common/utils/ds/seq_arr.h"
#include "openair2/E1AP/e1ap_common.h"
#include "openair2/LAYER2/NR_MAC_gNB/nr_mac_gNB.h"
#include "openair2/F1AP/f1ap_ids.h"
#include "openair2/RRC/NR/nr_rrc_defs.h"
#include "openair2/RRC/NR/rrc_gNB_UE_context.h"
#include "ran_e2sm_ue_id.h"
#include "ran_func_kpm_subs.h"

#include <assert.h>
#include <pthread.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

RAN_CONTEXT_t RC;
get_ue_id fill_ue_id_data[END_NGRAN_NODE_TYPE] = {0};

int64_t time_now_us(void)
{
  return 1;
}

char *get_ngran_name(ngran_node_t node_type)
{
  (void)node_type;
  return "gNB";
}

rrc_gNB_ue_context_t *rrc_gNB_get_ue_context_by_rnti(gNB_RRC_INST *rrc, sctp_assoc_t assoc_id, rnti_t rnti)
{
  (void)rrc;
  (void)assoc_id;
  (void)rnti;
  return NULL;
}

struct rrc_gNB_ue_context_s *rrc_nr_ue_tree_s_RB_MINMAX(struct rrc_nr_ue_tree_s *tree, int val)
{
  (void)tree;
  (void)val;
  return NULL;
}

struct rrc_gNB_ue_context_s *rrc_nr_ue_tree_s_RB_NEXT(struct rrc_gNB_ue_context_s *ue)
{
  (void)ue;
  return NULL;
}

f1_ue_data_t du_get_f1_ue_data(uint32_t ue_id)
{
  (void)ue_id;
  return (f1_ue_data_t){0};
}

e1ap_upcp_inst_t *getCxtE1(instance_t instance)
{
  (void)instance;
  return NULL;
}

int nr_pdcp_get_num_ues(ue_id_t *ue_list, int len)
{
  (void)ue_list;
  (void)len;
  return 0;
}

size_t seq_arr_size(const seq_arr_t *arr)
{
  (void)arr;
  return 0;
}

void *seq_arr_front(const seq_arr_t *arr)
{
  (void)arr;
  return NULL;
}

void *seq_arr_next(const seq_arr_t *arr, const void *it)
{
  (void)arr;
  (void)it;
  return NULL;
}

void *seq_arr_end(const seq_arr_t *arr)
{
  (void)arr;
  return NULL;
}

void *seq_arr_at(const seq_arr_t *arr, uint32_t pos)
{
  (void)arr;
  (void)pos;
  return NULL;
}

ue_id_e2sm_t cp_ue_id_e2sm(const ue_id_e2sm_t *src)
{
  (void)src;
  return (ue_id_e2sm_t){0};
}

meas_info_format_1_lst_t cp_meas_info_format_1_lst(const meas_info_format_1_lst_t *src)
{
  meas_info_format_1_lst_t dst = {.meas_type.type = src->meas_type.type};
  dst.meas_type.name.len = src->meas_type.name.len;
  dst.meas_type.name.buf = malloc(dst.meas_type.name.len);
  assert(dst.meas_type.name.buf != NULL);
  memcpy(dst.meas_type.name.buf, src->meas_type.name.buf, dst.meas_type.name.len);
  return dst;
}

void init_kpm_subs_data(void)
{
}

e2_node_level_stats_t cp_node_level_stats(const e2_node_level_stats_t *src)
{
  return *src;
}

meas_record_lst_t get_kpm_meas_value(char *name,
                                     uint32_t gran_period_ms,
                                     cudu_ue_info_pair_t ue_info,
                                     size_t ue_idx,
                                     e2_node_level_stats_t *node_stats)
{
  (void)name;
  (void)gran_period_ms;
  (void)ue_info;
  (void)ue_idx;
  (void)node_stats;
  assert(false && "cell reports must not use the UE measurement path");
  return (meas_record_lst_t){0};
}

static bool name_is(const byte_array_t name, const char *expected)
{
  const size_t len = strlen(expected);
  return name.len == len && memcmp(name.buf, expected, len) == 0;
}

static meas_info_format_1_lst_t measurement(const char *name)
{
  meas_info_format_1_lst_t info = {0};
  info.meas_type.type = NAME_MEAS_TYPE;
  info.meas_type.name = cp_str_to_ba(name);
  return info;
}

static void free_action_definition(kpm_act_def_t *action)
{
  for (size_t i = 0; i < action->frm_1.meas_info_lst_len; ++i)
    free(action->frm_1.meas_info_lst[i].meas_type.name.buf);
  free(action->frm_1.meas_info_lst);
}

static void assert_cell_style_1_emits_format_1_report(void)
{
  gNB_RRC_INST rrc = {.node_type = ngran_gNB};
  gNB_RRC_INST *rrc_instances[] = {&rrc};
  RC.nrrrc = rrc_instances;

  gNB_MAC_INST mac = {0};
  assert(pthread_mutex_init(&mac.sched_lock, NULL) == 0);
  gNB_MAC_INST *mac_instances[] = {&mac};
  RC.nrmac = mac_instances;

  kpm_act_def_t action = {.type = FORMAT_1_ACTION_DEFINITION};
  action.frm_1.gran_period_ms = 1000;
  action.frm_1.meas_info_lst_len = 2;
  action.frm_1.meas_info_lst = calloc(action.frm_1.meas_info_lst_len, sizeof(*action.frm_1.meas_info_lst));
  assert(action.frm_1.meas_info_lst != NULL);
  action.frm_1.meas_info_lst[0] = measurement("RRU.PrbTotDl");
  action.frm_1.meas_info_lst[1] = measurement("RRU.PrbTotUl");

  kpm_rd_ind_data_t report = {.act_def = &action};
  assert(read_kpm_sm(&report));

  assert(report.ind.hdr.type == FORMAT_1_INDICATION_HEADER);
  assert(report.ind.msg.type == FORMAT_1_INDICATION_MESSAGE);
  assert(report.ind.msg.frm_1.meas_data_lst_len == 1);
  assert(report.ind.msg.frm_1.meas_data_lst[0].meas_record_len == 2);
  assert(report.ind.msg.frm_1.meas_data_lst[0].meas_record_lst[0].value == NO_VALUE_MEAS_VALUE);
  assert(report.ind.msg.frm_1.meas_data_lst[0].meas_record_lst[1].value == NO_VALUE_MEAS_VALUE);
  assert(report.ind.msg.frm_1.meas_info_lst_len == 2);
  assert(name_is(report.ind.msg.frm_1.meas_info_lst[0].meas_type.name, "RRU.PrbTotDl"));
  assert(name_is(report.ind.msg.frm_1.meas_info_lst[1].meas_type.name, "RRU.PrbTotUl"));

  free_action_definition(&action);
  assert(pthread_mutex_destroy(&mac.sched_lock) == 0);
}

int main(void)
{
  assert_cell_style_1_emits_format_1_report();
  return 0;
}
