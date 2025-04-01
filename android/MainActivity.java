package ai.alphaedge.stockanalysis;

import android.content.Intent;
import android.os.Bundle;
import android.view.MenuItem;
import android.view.View;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.appcompat.app.ActionBarDrawerToggle;
import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.widget.Toolbar;
import androidx.core.view.GravityCompat;
import androidx.drawerlayout.widget.DrawerLayout;

import com.google.android.material.navigation.NavigationView;

/**
 * Main Activity for AlphaEdge.ai Android App
 * This activity serves as the entry point and navigation hub for the app.
 */
public class MainActivity extends AppCompatActivity 
        implements NavigationView.OnNavigationItemSelectedListener {
    
    private DrawerLayout drawer;
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        
        // Set up the toolbar
        Toolbar toolbar = findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);
        
        // Set up the navigation drawer
        drawer = findViewById(R.id.drawer_layout);
        NavigationView navigationView = findViewById(R.id.nav_view);
        navigationView.setNavigationItemSelectedListener(this);
        
        ActionBarDrawerToggle toggle = new ActionBarDrawerToggle(
                this, drawer, toolbar, R.string.navigation_drawer_open, R.string.navigation_drawer_close);
        drawer.addDrawerListener(toggle);
        toggle.syncState();
        
        // Set default fragment if this is the first time the activity is created
        if (savedInstanceState == null) {
            getSupportFragmentManager().beginTransaction()
                    .replace(R.id.fragment_container, new DashboardFragment())
                    .commit();
            navigationView.setCheckedItem(R.id.nav_dashboard);
            setTitle(R.string.menu_dashboard);
        }
        
        // Set up user info in the navigation header
        View headerView = navigationView.getHeaderView(0);
        TextView tvUsername = headerView.findViewById(R.id.nav_header_username);
        TextView tvEmail = headerView.findViewById(R.id.nav_header_email);
        
        // In a real app, these would be fetched from a user session
        tvUsername.setText("Demo User");
        tvEmail.setText("demo@alphaedge.ai");
    }
    
    @Override
    public boolean onNavigationItemSelected(@NonNull MenuItem item) {
        // Handle navigation view item clicks
        switch (item.getItemId()) {
            case R.id.nav_dashboard:
                getSupportFragmentManager().beginTransaction()
                        .replace(R.id.fragment_container, new DashboardFragment())
                        .commit();
                setTitle(R.string.menu_dashboard);
                break;
            case R.id.nav_portfolio:
                Intent portfolioIntent = new Intent(this, PortfolioActivity.class);
                startActivity(portfolioIntent);
                break;
            case R.id.nav_stock_analysis:
                Intent analysisIntent = new Intent(this, StockAnalysisActivity.class);
                startActivity(analysisIntent);
                break;
            case R.id.nav_recommendations:
                Intent recommendationsIntent = new Intent(this, RecommendationsActivity.class);
                startActivity(recommendationsIntent);
                break;
            case R.id.nav_profile:
                Intent profileIntent = new Intent(this, ProfileActivity.class);
                startActivity(profileIntent);
                break;
            case R.id.nav_help:
                Intent helpIntent = new Intent(this, HelpActivity.class);
                startActivity(helpIntent);
                break;
            case R.id.nav_logout:
                // Handle logout
                // In a real app, this would clear user session and redirect to login
                finish();
                break;
        }
        
        drawer.closeDrawer(GravityCompat.START);
        return true;
    }
    
    @Override
    public void onBackPressed() {
        if (drawer.isDrawerOpen(GravityCompat.START)) {
            drawer.closeDrawer(GravityCompat.START);
        } else {
            super.onBackPressed();
        }
    }
}