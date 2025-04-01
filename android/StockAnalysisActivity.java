package ai.alphaedge.stockanalysis;

import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.widget.Toolbar;

import com.github.mikephil.charting.charts.CandleStickChart;
import com.github.mikephil.charting.components.XAxis;
import com.github.mikephil.charting.components.YAxis;
import com.github.mikephil.charting.data.CandleData;
import com.github.mikephil.charting.data.CandleDataSet;
import com.github.mikephil.charting.data.CandleEntry;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.Executor;
import java.util.concurrent.Executors;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;
import retrofit2.Retrofit;
import retrofit2.converter.gson.GsonConverterFactory;

/**
 * Stock Analysis Activity for AlphaEdge.ai Android App
 * This activity allows users to search for and analyze stocks.
 */
public class StockAnalysisActivity extends AppCompatActivity {
    
    private EditText etStockSearch;
    private Button btnSearch;
    private ProgressBar progressBar;
    private LinearLayout analysisResultsContainer;
    private CandleStickChart priceChart;
    private TextView tvStockName;
    private TextView tvCurrentPrice;
    private TextView tvTechnicalScore;
    private TextView tvFundamentalScore;
    private TextView tvBehavioralScore;
    private TextView tvOverallScore;
    private TextView tvRecommendation;
    private LinearLayout indicatorsContainer;
    
    private final Executor executor = Executors.newSingleThreadExecutor();
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_stock_analysis);
        
        // Set up toolbar
        Toolbar toolbar = findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);
        getSupportActionBar().setDisplayHomeAsUpEnabled(true);
        
        // Initialize views
        etStockSearch = findViewById(R.id.et_stock_search);
        btnSearch = findViewById(R.id.btn_search);
        progressBar = findViewById(R.id.progress_bar);
        analysisResultsContainer = findViewById(R.id.container_analysis_results);
        priceChart = findViewById(R.id.chart_price);
        tvStockName = findViewById(R.id.tv_stock_name);
        tvCurrentPrice = findViewById(R.id.tv_current_price);
        tvTechnicalScore = findViewById(R.id.tv_technical_score);
        tvFundamentalScore = findViewById(R.id.tv_fundamental_score);
        tvBehavioralScore = findViewById(R.id.tv_behavioral_score);
        tvOverallScore = findViewById(R.id.tv_overall_score);
        tvRecommendation = findViewById(R.id.tv_recommendation);
        indicatorsContainer = findViewById(R.id.container_indicators);
        
        // Hide results container initially
        analysisResultsContainer.setVisibility(View.GONE);
        
        // Set up search button click listener
        btnSearch.setOnClickListener(v -> {
            String ticker = etStockSearch.getText().toString().trim();
            if (ticker.isEmpty()) {
                Toast.makeText(this, "Please enter a stock symbol", Toast.LENGTH_SHORT).show();
                return;
            }
            
            // Show progress and hide results
            progressBar.setVisibility(View.VISIBLE);
            analysisResultsContainer.setVisibility(View.GONE);
            
            // Perform stock analysis
            performStockAnalysis(ticker);
        });
    }
    
    /**
     * Performs stock analysis for the given ticker.
     * In a real app, this would make API calls to fetch data.
     * 
     * @param ticker Stock ticker symbol
     */
    private void performStockAnalysis(String ticker) {
        // Simulate network delay
        executor.execute(() -> {
            try {
                // In a real app, this would be a network call
                Thread.sleep(1500);
                
                // Update UI on main thread
                runOnUiThread(() -> {
                    progressBar.setVisibility(View.GONE);
                    analysisResultsContainer.setVisibility(View.VISIBLE);
                    
                    // Set sample data for demonstration
                    if (ticker.equalsIgnoreCase("RELIANCE") || ticker.equalsIgnoreCase("TCS") ||
                            ticker.equalsIgnoreCase("INFY")) {
                        displayAnalysisResults(ticker);
                    } else {
                        // For demo purposes, show error for other tickers
                        Toast.makeText(this, "Stock not found. Try RELIANCE, TCS, or INFY for demo", 
                                Toast.LENGTH_LONG).show();
                    }
                });
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        });
    }
    
    /**
     * Displays analysis results for a given ticker.
     * In a real app, this would use data from API responses.
     * 
     * @param ticker Stock ticker symbol
     */
    private void displayAnalysisResults(String ticker) {
        // Sample data for demonstration
        String stockName;
        double currentPrice;
        double technicalScore;
        double fundamentalScore;
        double behavioralScore;
        String recommendation;
        
        // Set sample data based on ticker
        switch (ticker.toUpperCase()) {
            case "RELIANCE":
                stockName = "Reliance Industries Ltd";
                currentPrice = 2600.75;
                technicalScore = 7.8;
                fundamentalScore = 8.2;
                behavioralScore = 6.9;
                recommendation = "BUY";
                break;
            case "TCS":
                stockName = "Tata Consultancy Services Ltd";
                currentPrice = 3350.20;
                technicalScore = 6.5;
                fundamentalScore = 8.5;
                behavioralScore = 7.2;
                recommendation = "HOLD";
                break;
            case "INFY":
                stockName = "Infosys Ltd";
                currentPrice = 1505.30;
                technicalScore = 8.1;
                fundamentalScore = 7.5;
                behavioralScore = 7.8;
                recommendation = "BUY";
                break;
            default:
                stockName = "Unknown";
                currentPrice = 0.0;
                technicalScore = 0.0;
                fundamentalScore = 0.0;
                behavioralScore = 0.0;
                recommendation = "UNKNOWN";
        }
        
        // Calculate overall score
        double overallScore = (technicalScore + fundamentalScore + behavioralScore) / 3;
        
        // Update UI
        tvStockName.setText(stockName + " (" + ticker.toUpperCase() + ")");
        tvCurrentPrice.setText(String.format("₹%.2f", currentPrice));
        tvTechnicalScore.setText(String.format("%.1f/10", technicalScore));
        tvFundamentalScore.setText(String.format("%.1f/10", fundamentalScore));
        tvBehavioralScore.setText(String.format("%.1f/10", behavioralScore));
        tvOverallScore.setText(String.format("%.1f/10", overallScore));
        tvRecommendation.setText(recommendation);
        
        // Set recommendation color
        if (recommendation.equals("BUY") || recommendation.equals("STRONG BUY")) {
            tvRecommendation.setTextColor(getResources().getColor(R.color.colorGreen));
        } else if (recommendation.equals("SELL") || recommendation.equals("STRONG SELL")) {
            tvRecommendation.setTextColor(getResources().getColor(R.color.colorRed));
        } else {
            tvRecommendation.setTextColor(getResources().getColor(R.color.colorOrange));
        }
        
        // Set up price chart with sample data
        setupPriceChart();
        
        // Set up indicator cards with sample data
        setupIndicatorCards();
    }
    
    /**
     * Sets up the price chart with sample data.
     * In a real app, this would use historical data from an API.
     */
    private void setupPriceChart() {
        List<CandleEntry> entries = new ArrayList<>();
        
        // Sample data (in a real app, this would come from API)
        entries.add(new CandleEntry(0, 2650f, 2550f, 2580f, 2610f));
        entries.add(new CandleEntry(1, 2630f, 2540f, 2590f, 2600f));
        entries.add(new CandleEntry(2, 2620f, 2530f, 2550f, 2590f));
        entries.add(new CandleEntry(3, 2610f, 2520f, 2520f, 2580f));
        entries.add(new CandleEntry(4, 2600f, 2510f, 2590f, 2570f));
        entries.add(new CandleEntry(5, 2590f, 2500f, 2560f, 2560f));
        entries.add(new CandleEntry(6, 2580f, 2490f, 2580f, 2550f));
        entries.add(new CandleEntry(7, 2570f, 2480f, 2480f, 2540f));
        entries.add(new CandleEntry(8, 2560f, 2470f, 2550f, 2530f));
        entries.add(new CandleEntry(9, 2550f, 2460f, 2480f, 2520f));
        
        CandleDataSet dataSet = new CandleDataSet(entries, "Stock Price");
        dataSet.setColor(getResources().getColor(R.color.colorPrimary));
        dataSet.setShadowColor(getResources().getColor(R.color.colorGrey));
        dataSet.setShadowWidth(0.7f);
        dataSet.setDecreasingColor(getResources().getColor(R.color.colorRed));
        dataSet.setDecreasingPaintStyle(android.graphics.Paint.Style.FILL);
        dataSet.setIncreasingColor(getResources().getColor(R.color.colorGreen));
        dataSet.setIncreasingPaintStyle(android.graphics.Paint.Style.FILL);
        dataSet.setNeutralColor(getResources().getColor(R.color.colorGrey));
        
        CandleData data = new CandleData(dataSet);
        
        priceChart.setData(data);
        priceChart.getDescription().setEnabled(false);
        priceChart.setDragEnabled(true);
        priceChart.setScaleEnabled(true);
        
        XAxis xAxis = priceChart.getXAxis();
        xAxis.setPosition(XAxis.XAxisPosition.BOTTOM);
        
        YAxis leftAxis = priceChart.getAxisLeft();
        leftAxis.setDrawGridLines(false);
        
        priceChart.getAxisRight().setEnabled(false);
        priceChart.getLegend().setEnabled(false);
        
        priceChart.invalidate();
    }
    
    /**
     * Sets up the technical indicator cards with sample data.
     * In a real app, this would use calculated indicators from an API.
     */
    private void setupIndicatorCards() {
        // Clear existing cards
        indicatorsContainer.removeAllViews();
        
        // Add sample indicator cards
        addIndicatorCard("RSI (14)", "62.5", "Neutral", R.color.colorOrange);
        addIndicatorCard("MACD", "Bullish Crossover", "Bullish", R.color.colorGreen);
        addIndicatorCard("Moving Avg (50,200)", "Above", "Bullish", R.color.colorGreen);
        addIndicatorCard("Bollinger Bands", "Middle Band", "Neutral", R.color.colorOrange);
        addIndicatorCard("ADX", "28.6", "Strong Trend", R.color.colorGreen);
    }
    
    /**
     * Adds an indicator card to the indicators container.
     * 
     * @param name Indicator name
     * @param value Indicator value
     * @param signal Signal (Bullish, Bearish, Neutral)
     * @param signalColorResId Color resource ID for the signal
     */
    private void addIndicatorCard(String name, String value, String signal, int signalColorResId) {
        View card = getLayoutInflater().inflate(R.layout.card_indicator, indicatorsContainer, false);
        
        TextView tvName = card.findViewById(R.id.tv_indicator_name);
        TextView tvValue = card.findViewById(R.id.tv_indicator_value);
        TextView tvSignal = card.findViewById(R.id.tv_indicator_signal);
        
        tvName.setText(name);
        tvValue.setText(value);
        tvSignal.setText(signal);
        tvSignal.setTextColor(getResources().getColor(signalColorResId));
        
        indicatorsContainer.addView(card);
    }
    
    @Override
    public boolean onSupportNavigateUp() {
        onBackPressed();
        return true;
    }
}