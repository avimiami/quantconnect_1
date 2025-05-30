## example of how to use the strategies:

# Import the strategies
from strategies.entries.low_volatility_entry import LowVolatilityEntry
from strategies.entries.value_entry import ValueEntry
from strategies.exits.exit_macd_cross import ExitMACDCross
from strategies.exits.exit_drawdown_limit import ExitDrawdownLimit
from strategies.exits.exit_rebalance_date import ExitRebalanceDate

# Initialize the strategies
low_vol_entry = LowVolatilityEntry(volatility_threshold=0.015)
value_entry = ValueEntry(pe_threshold=18, pb_threshold=2.5)
macd_exit = ExitMACDCross()
drawdown_exit = ExitDrawdownLimit(max_drawdown=-0.07)  # 7% drawdown limit
rebalance_exit = ExitRebalanceDate(rebalance_freq='quarterly')

# Use them in your trading logic
entry_signal = low_vol_entry.get_latest_signal(data)
if entry_signal['entry_long']:
    # Enter a long position
    pass

# Check exit conditions
exit_signal_macd = macd_exit.get_latest_signal(data, position_type="long")
exit_signal_drawdown = drawdown_exit.get_latest_signal(data, position_type="long", entry_price=entry_price)
exit_signal_rebalance = rebalance_exit.get_latest_signal(data)

if exit_signal_macd['exit_signal'] or exit_signal_drawdown['exit_signal'] or exit_signal_rebalance['exit_signal']:
    # Exit the position
    pass