from __future__ import division

import timeseries
import utils
import positions
import plotting
import internals

import numpy as np
import pandas as pd

def create_returns_tear_sheet(df_rets, warm_up_days_pct=0.5):
    benchmark_rets = utils.get_symbol_rets('SPY')
    benchmark2_rets = utils.get_symbol_rets('IEF')  #7-10yr Bond ETF.

    # if your directory structure isn't exactly the same as the research server you can manually specify the location
    # of the directory holding the risk factor data
    #risk_factors = load_portfolio_risk_factors(local_risk_factor_path)
    risk_factors = internals.load_portfolio_risk_factors().dropna(axis=0)

    plotting.set_plot_defaults()

    algo_ts = timeseries.cum_returns(df_rets, starting_value=1)

    print "Entire data start date: " + str(algo_ts.index[0])
    print "Entire data end date: " + str(algo_ts.index[-1])

    algo_create_date = df_rets.index[ int(len(df_rets)*warm_up_days_pct) ]

    print '\n'

    plotting.show_perf_stats(df_rets, algo_create_date, benchmark_rets)

    plotting.plot_rolling_returns(algo_ts, df_rets, benchmark_rets, benchmark2_rets, algo_create_date)

    plotting.plot_rolling_beta(algo_ts, df_rets, benchmark_rets)

    plotting.plot_rolling_sharp(algo_ts, df_rets)

    plotting.plot_rolling_risk_factors(algo_ts, df_rets, risk_factors, legend_loc='best')

    plotting.plot_calendar_returns_info_graphic(df_rets)

    df_weekly = timeseries.aggregate_returns(df_rets, 'weekly')
    df_monthly = timeseries.aggregate_returns(df_rets, 'monthly')

    plotting.plot_return_quantiles(df_rets, df_weekly, df_monthly)

    plotting.show_return_range(df_rets, df_weekly)

    # Get interesting time periods

    plotting.plot_interesting_times(df_rets, benchmark_rets)

    #########################
    # Drawdowns

    try:
        plot_drawdowns(df_rets, top=5)
        print '\nWorst Drawdown Periods'
        drawdown_df = gen_drawdown_table(df_rets, top=5)
        drawdown_df['peak date'] = pd.to_datetime(drawdown_df['peak date'],unit='D')
        drawdown_df['valley date'] = pd.to_datetime(drawdown_df['valley date'],unit='D')
        drawdown_df['recovery date'] = pd.to_datetime(drawdown_df['recovery date'],unit='D')
        print drawdown_df
    except:
        pass


def create_position_tear_sheet(df_rets, df_pos_val, gross_lev=None):
    algo_ts = timeseries.cum_returns(df_rets, starting_value=1)

    plotting.plot_gross_leverage(algo_ts, gross_lev)

    df_pos_alloc = positions.get_portfolio_alloc(df_pos_val)

    plotting.plot_exposures(algo_ts, df_pos_alloc)

    plotting.show_and_plot_top_positions(algo_ts, df_pos_alloc)

    plotting.plot_holdings(df_pos_alloc)


def create_txn_tear_sheet(df_rets, df_pos_val, df_txn):
    algo_ts = timeseries.cum_returns(df_rets, starting_value=1)

    plotting.plot_daily_turnover(algo_ts, df_txn, df_pos_val)

    plotting.plot_daily_volume(algo_ts, df_txn)

    plotting.plot_volume_per_day_hist(algo_ts, df_txn)


def create_full_tear_sheet(df_rets, df_pos=None, df_txn=None,
                           gross_lev=None, fetcher_urls='',
                           algo_create_date=None):

    create_returns_tear_sheet(df_rets)

    if df_pos is not None:
        create_position_tear_sheet(df_rets, df_pos, gross_lev=gross_lev)

        if df_txn is not None:
            create_txn_tear_sheet(df_rets, df_pos, df_txn)