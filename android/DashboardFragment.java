package ai.alphaedge.stockanalysis;

import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.github.mikephil.charting.charts.PieChart;
import com.github.mikephil.charting.data.PieData;
import com.github.mikephil.charting.data.PieDataSet;
import com.github.mikephil.charting.data.PieEntry;
import com.github.mikephil.charting.utils.ColorTemplate;

import java.util.ArrayList;
import java.util.List;

/**
 * Dashboard Fragment for AlphaEdge.ai Android App
 * This fragment displays the portfolio dashboard with sector allocation and performance metrics.
 */
public class DashboardFragment extends Fragment {
    
    private PieChart sectorAllocationChart;
    private RecyclerView holdingsRecyclerView;
    private TextView tvPortfolioValue;
    private TextView tvDailyChange;
    private TextView tvTotalReturn;
    
    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, 
                             @Nullable Bundle savedInstanceState) {
        View view = inflater.inflate(R.layout.fragment_dashboard, container, false);
        
        // Initialize views
        sectorAllocationChart = view.findViewById(R.id.pie_chart_sector_allocation);
        holdingsRecyclerView = view.findViewById(R.id.recycler_view_holdings);
        tvPortfolioValue = view.findViewById(R.id.tv_portfolio_value);
        tvDailyChange = view.findViewById(R.id.tv_daily_change);
        tvTotalReturn = view.findViewById(R.id.tv_total_return);
        
        // Set up sector allocation chart
        setupSectorAllocationChart();
        
        // Set up holdings recycler view
        setupHoldingsRecyclerView();
        
        // Set portfolio metrics
        tvPortfolioValue.setText("₹1,250,000");
        tvDailyChange.setText("+₹15,000 (1.2%)");
        tvTotalReturn.setText("+₹125,000 (10%)");
        
        return view;
    }
    
    /**
     * Sets up the sector allocation pie chart with sample data.
     * In a real app, this would use data from an API or local database.
     */
    private void setupSectorAllocationChart() {
        List<PieEntry> entries = new ArrayList<>();
        
        // Sample data (in a real app, this would come from API)
        entries.add(new PieEntry(30f, "Technology"));
        entries.add(new PieEntry(20f, "Financial"));
        entries.add(new PieEntry(15f, "Healthcare"));
        entries.add(new PieEntry(10f, "Consumer"));
        entries.add(new PieEntry(10f, "Energy"));
        entries.add(new PieEntry(15f, "Others"));
        
        PieDataSet dataSet = new PieDataSet(entries, "Sector Allocation");
        dataSet.setColors(ColorTemplate.MATERIAL_COLORS);
        
        PieData data = new PieData(dataSet);
        sectorAllocationChart.setData(data);
        sectorAllocationChart.getDescription().setEnabled(false);
        sectorAllocationChart.setCenterText("Sectors");
        sectorAllocationChart.animate();
    }
    
    /**
     * Sets up the holdings recycler view with sample data.
     * In a real app, this would use data from an API or local database.
     */
    private void setupHoldingsRecyclerView() {
        List<HoldingItem> holdings = new ArrayList<>();
        
        // Sample data (in a real app, this would come from API)
        holdings.add(new HoldingItem("RELIANCE", "Reliance Industries", 50, 2500.0, 2600.0, 4.0));
        holdings.add(new HoldingItem("TCS", "Tata Consultancy Services", 20, 3200.0, 3350.0, 4.7));
        holdings.add(new HoldingItem("INFY", "Infosys Limited", 30, 1450.0, 1500.0, 3.4));
        holdings.add(new HoldingItem("HDFCBANK", "HDFC Bank", 25, 1600.0, 1580.0, -1.25));
        holdings.add(new HoldingItem("SBIN", "State Bank of India", 100, 520.0, 548.0, 5.4));
        
        HoldingsAdapter adapter = new HoldingsAdapter(holdings);
        holdingsRecyclerView.setAdapter(adapter);
        holdingsRecyclerView.setLayoutManager(new LinearLayoutManager(getContext()));
    }
    
    /**
     * Model class for holding items in the recycler view.
     */
    private static class HoldingItem {
        String symbol;
        String name;
        int quantity;
        double buyPrice;
        double currentPrice;
        double changePercent;
        
        HoldingItem(String symbol, String name, int quantity, double buyPrice, 
                    double currentPrice, double changePercent) {
            this.symbol = symbol;
            this.name = name;
            this.quantity = quantity;
            this.buyPrice = buyPrice;
            this.currentPrice = currentPrice;
            this.changePercent = changePercent;
        }
    }
    
    /**
     * Adapter for holdings recycler view.
     */
    private static class HoldingsAdapter extends RecyclerView.Adapter<HoldingsAdapter.ViewHolder> {
        private List<HoldingItem> holdings;
        
        HoldingsAdapter(List<HoldingItem> holdings) {
            this.holdings = holdings;
        }
        
        @NonNull
        @Override
        public ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
            View view = LayoutInflater.from(parent.getContext())
                    .inflate(R.layout.item_holding, parent, false);
            return new ViewHolder(view);
        }
        
        @Override
        public void onBindViewHolder(@NonNull ViewHolder holder, int position) {
            HoldingItem item = holdings.get(position);
            
            holder.tvSymbol.setText(item.symbol);
            holder.tvName.setText(item.name);
            holder.tvQuantity.setText(String.valueOf(item.quantity));
            holder.tvCurrentPrice.setText(String.format("₹%.2f", item.currentPrice));
            
            String changeText = String.format("%.2f%%", item.changePercent);
            if (item.changePercent >= 0) {
                changeText = "+" + changeText;
                holder.tvChange.setTextColor(holder.itemView.getContext()
                        .getResources().getColor(R.color.colorGreen));
            } else {
                holder.tvChange.setTextColor(holder.itemView.getContext()
                        .getResources().getColor(R.color.colorRed));
            }
            holder.tvChange.setText(changeText);
        }
        
        @Override
        public int getItemCount() {
            return holdings.size();
        }
        
        static class ViewHolder extends RecyclerView.ViewHolder {
            TextView tvSymbol;
            TextView tvName;
            TextView tvQuantity;
            TextView tvCurrentPrice;
            TextView tvChange;
            
            ViewHolder(@NonNull View itemView) {
                super(itemView);
                tvSymbol = itemView.findViewById(R.id.tv_symbol);
                tvName = itemView.findViewById(R.id.tv_name);
                tvQuantity = itemView.findViewById(R.id.tv_quantity);
                tvCurrentPrice = itemView.findViewById(R.id.tv_current_price);
                tvChange = itemView.findViewById(R.id.tv_change);
            }
        }
    }
}