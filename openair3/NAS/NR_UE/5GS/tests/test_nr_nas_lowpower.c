#include <assert.h>
#include <stdbool.h>

#include "nr_nas_lowpower.h"

static void test_psm_init_disables_timers(void)
{
  nr_ue_nas_t nas = {0};

  nr_nas_psm_init(&nas);

  assert(nas.t3324 == -1);
  assert(nas.t3512 == -1);
  assert(!nas.psm_configured);
  assert(!nas.psm_active_time_expired);
}

static void test_psm_timer_update_tracks_active_time(void)
{
  nr_ue_nas_t nas = {0};
  nr_nas_psm_init(&nas);

  nr_nas_psm_update_timers(&nas, 30, 3600);

  assert(nas.t3324 == 30);
  assert(nas.t3512 == 3600);
  assert(nas.psm_configured);
  assert(!nas.psm_active_time_expired);
}

static void test_psm_ready_requires_registered_idle_and_expired_active_time(void)
{
  nr_ue_nas_t nas = {0};
  nr_nas_psm_init(&nas);
  nr_nas_psm_update_timers(&nas, 30, 3600);

  nas.fiveGMM_state = FGS_REGISTERED;
  nas.fiveGMM_mode = FGS_CONNECTED;
  nr_nas_psm_mark_active_time_expired(&nas);
  assert(!nr_nas_psm_low_power_ready(&nas));

  nas.fiveGMM_mode = FGS_IDLE;
  assert(nr_nas_psm_low_power_ready(&nas));
}

int main(void)
{
  test_psm_init_disables_timers();
  test_psm_timer_update_tracks_active_time();
  test_psm_ready_requires_registered_idle_and_expired_active_time();
  return 0;
}
