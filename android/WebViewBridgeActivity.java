package ai.alphaedge.stockanalysis;

import android.annotation.SuppressLint;
import android.os.Bundle;
import android.webkit.JavascriptInterface;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.widget.Toolbar;

import org.json.JSONException;
import org.json.JSONObject;

/**
 * WebView Bridge Activity for AlphaEdge.ai Android App
 * This activity provides a bridge between the native Android app and the web application.
 * It allows parts of the app to be implemented using the same web logic as the Streamlit app
 * when needed, while maintaining the native look and feel for most of the app.
 */
public class WebViewBridgeActivity extends AppCompatActivity {
    
    private WebView webView;
    private String feature;
    
    @SuppressLint("SetJavaScriptEnabled")
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_webview_bridge);
        
        // Set up toolbar
        Toolbar toolbar = findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);
        getSupportActionBar().setDisplayHomeAsUpEnabled(true);
        
        // Get the feature to load from intent
        feature = getIntent().getStringExtra("feature");
        if (feature == null) {
            feature = "dashboard"; // Default feature
        }
        
        // Set title based on feature
        setTitleForFeature(feature);
        
        // Initialize WebView
        webView = findViewById(R.id.web_view);
        WebSettings webSettings = webView.getSettings();
        webSettings.setJavaScriptEnabled(true);
        webSettings.setDomStorageEnabled(true);
        
        // Add JavaScript interface for communication between WebView and Android
        webView.addJavascriptInterface(new WebAppInterface(), "AndroidBridge");
        
        // Set WebViewClient to handle page navigation
        webView.setWebViewClient(new WebViewClient() {
            @Override
            public void onPageFinished(WebView view, String url) {
                super.onPageFinished(view, url);
                
                // Inject script to hide web app header and navigation
                webView.evaluateJavascript(
                        "document.querySelector('.stApp > header').style.display = 'none';" +
                        "document.querySelector('.sidebar .sidebar-content').style.display = 'none';", 
                        null);
                
                // Navigate to the correct page based on feature
                if (!feature.equals("dashboard")) {
                    webView.evaluateJavascript(
                            "window.location.href = '/" + feature + "';", 
                            null);
                }
            }
        });
        
        // Load the web app
        webView.loadUrl("https://alphaedge.streamlit.app");
    }
    
    /**
     * Sets the activity title based on the feature.
     * 
     * @param feature Feature identifier
     */
    private void setTitleForFeature(String feature) {
        switch (feature) {
            case "dashboard":
                setTitle("Portfolio Dashboard");
                break;
            case "stock_analysis":
                setTitle("Stock Analysis");
                break;
            case "recommendations":
                setTitle("Recommendations");
                break;
            case "portfolio":
                setTitle("Portfolio Management");
                break;
            case "profile":
                setTitle("User Profile");
                break;
            case "help":
                setTitle("Help & Support");
                break;
            default:
                setTitle("AlphaEdge.ai");
        }
    }
    
    /**
     * JavaScript interface to enable communication between WebView JavaScript and Android native code.
     */
    private class WebAppInterface {
        
        /**
         * Shows a toast message from JavaScript.
         * 
         * @param message Message to display
         */
        @JavascriptInterface
        public void showToast(String message) {
            runOnUiThread(() -> Toast.makeText(WebViewBridgeActivity.this, message, Toast.LENGTH_SHORT).show());
        }
        
        /**
         * Gets data from native Android app to be used in web app.
         * 
         * @param dataType Type of data requested
         * @return JSON string with the requested data
         */
        @JavascriptInterface
        public String getData(String dataType) {
            JSONObject jsonData = new JSONObject();
            
            try {
                switch (dataType) {
                    case "user":
                        // Sample user data
                        jsonData.put("id", 1);
                        jsonData.put("username", "demo_user");
                        jsonData.put("email", "demo@alphaedge.ai");
                        break;
                    case "portfolio":
                        // Sample portfolio data - in a real app, this would be fetched from the app's database
                        jsonData.put("id", 1);
                        jsonData.put("name", "My Portfolio");
                        jsonData.put("value", 1250000);
                        jsonData.put("daily_change_percent", 1.2);
                        break;
                    default:
                        jsonData.put("error", "Unknown data type");
                }
            } catch (JSONException e) {
                e.printStackTrace();
            }
            
            return jsonData.toString();
        }
        
        /**
         * Sends data from web app to native Android app.
         * 
         * @param dataType Type of data being sent
         * @param jsonData JSON string with the data
         * @return Boolean string indicating success/failure
         */
        @JavascriptInterface
        public String sendData(String dataType, String jsonData) {
            try {
                JSONObject data = new JSONObject(jsonData);
                
                switch (dataType) {
                    case "add_stock":
                        // Process add stock request
                        String ticker = data.getString("ticker");
                        int quantity = data.getInt("quantity");
                        double price = data.getDouble("price");
                        
                        // In a real app, this would store the stock in the app's database
                        runOnUiThread(() -> {
                            Toast.makeText(WebViewBridgeActivity.this, 
                                    "Added " + quantity + " shares of " + ticker + " at ₹" + price,
                                    Toast.LENGTH_SHORT).show();
                        });
                        break;
                    case "update_profile":
                        // Process profile update request
                        // Similar implementation to above
                        break;
                }
                
                JSONObject response = new JSONObject();
                response.put("success", true);
                return response.toString();
                
            } catch (JSONException e) {
                e.printStackTrace();
                try {
                    JSONObject response = new JSONObject();
                    response.put("success", false);
                    response.put("error", e.getMessage());
                    return response.toString();
                } catch (JSONException ex) {
                    return "{\"success\": false, \"error\": \"JSON error\"}";
                }
            }
        }
        
        /**
         * Closes the WebView and returns to the native activity.
         */
        @JavascriptInterface
        public void close() {
            runOnUiThread(() -> finish());
        }
    }
    
    @Override
    public boolean onSupportNavigateUp() {
        onBackPressed();
        return true;
    }
}