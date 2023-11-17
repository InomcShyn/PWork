package com.example.pwork.view.vation;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.ImageButton;

import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.example.pwork.R;
import com.example.pwork.database.HikeDatabase;
import com.example.pwork.model.Obser;

import java.util.List;

public class Observations extends AppCompatActivity {

    private RecyclerView recyclerView;
    private Button btnNew;
    private ImageButton customButton;
    private ObserAdapter adapter;
    private HikeDatabase db;
    private BroadcastReceiver observationAddedReceiver;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_observations);

        db = HikeDatabase.getDatabase(this);

        recyclerView = findViewById(R.id.recyclerView);
        recyclerView.setLayoutManager(new LinearLayoutManager(this));

        customButton = findViewById(R.id.custom_button);
        customButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                finish(); //kết thúc EditHike và quay lại DetailsHike
            }
        });
        btnNew = findViewById(R.id.btnNew);
        btnNew.setOnClickListener(v -> {
            //mở một Activity hoặc Fragment để thêm quan sát mới
            Intent intent = new Intent(Observations.this, ObserAdd.class);
            startActivity(intent);
        });

        observationAddedReceiver = new BroadcastReceiver() {
            @Override
            public void onReceive(Context context, Intent intent) {
                loadObservations();
            }
        };
        registerReceiver(observationAddedReceiver, new IntentFilter("observation_added"));

        loadObservations();
    }

    private void loadObservations() {
        new Thread(() -> {
            //truy vấn cơ sở dữ liệu Room ở đây
            List<Obser> observations = db.observationDao().getAllObservations();

            //cập nhật UI trên luồng giao diện người dùng
            runOnUiThread(() -> {
                adapter = new ObserAdapter(this, observations, db);
                recyclerView.setAdapter(adapter);
            });
        }).start();
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        // Unregister the broadcast receiver when the activity is destroyed
        unregisterReceiver(observationAddedReceiver);
    }
}

