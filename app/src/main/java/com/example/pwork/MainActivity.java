package com.example.pwork;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.fragment.app.Fragment;
import android.os.Bundle;
import android.view.MenuItem;
import com.example.pwork.view.AddHike;
import com.example.pwork.view.DetailsHike;
import com.example.pwork.view.SearchHike;
import com.google.android.material.bottomnavigation.BottomNavigationView;

public class MainActivity extends AppCompatActivity {

    private AddHike addHike;
    private DetailsHike detailsHike;
    private SearchHike searchHike;
    private BottomNavigationView bottomNavigationView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // Khởi tạo các Fragment
        addHike = new AddHike();
        detailsHike = new DetailsHike();
        searchHike = new SearchHike();

        // Ánh xạ BottomNavigationView và thiết lập sự kiện chuyển đổi Fragment
        bottomNavigationView = findViewById(R.id.bottom_navigation);
        bottomNavigationView.setOnNavigationItemSelectedListener(new BottomNavigationView.OnNavigationItemSelectedListener() {
            @Override
            public boolean onNavigationItemSelected(@NonNull MenuItem item) {
                int itemId = item.getItemId();
                if (itemId == R.id.action_add) {
                    loadFragment(addHike);
                    return true;
                } else if (itemId == R.id.action_home) {
                    loadFragment(detailsHike);
                    return true;
                } else if (itemId == R.id.action_search) {
                    loadFragment(searchHike);
                    return true;
                }
                return false;
            }
        });

        // Hiển thị Fragment mặc định là AddHike
        if (savedInstanceState == null) {
            getSupportFragmentManager().beginTransaction().add(R.id.fragment_container, addHike).commit();
        }
    }

    // Phương thức để tải một Fragment mới
    private void loadFragment(Fragment fragment) {
        // Kiểm tra xem Fragment đã được thêm vào hay chưa
        if (!fragment.isAdded()) {
            getSupportFragmentManager().beginTransaction()
                    .add(R.id.fragment_container, fragment)
                    .commit();
        }

        getSupportFragmentManager().beginTransaction()
                .replace(R.id.fragment_container, fragment)
                .commit();
    }
}
