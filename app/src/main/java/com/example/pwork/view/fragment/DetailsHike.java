package com.example.pwork.view.fragment;

import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;

import androidx.fragment.app.Fragment;
import androidx.lifecycle.Observer;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.example.pwork.HikeAdapter;
import com.example.pwork.R;
import com.example.pwork.dao.HikeDao;
import com.example.pwork.database.HikeDatabase;
import com.example.pwork.model.Hike;

import java.util.ArrayList;
import java.util.List;

public class DetailsHike extends Fragment {

    private HikeAdapter adapter;
    private RecyclerView recyclerView;
    private HikeDatabase db;
    private HikeDao hikeDao;

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState) {
        View view = inflater.inflate(R.layout.fragment_details_hike, container, false);

        // Lấy thể hiện của HikeDatabase
        db = HikeDatabase.getDatabase(getActivity());


        recyclerView = view.findViewById(R.id.recyclerView);
        recyclerView.setLayoutManager(new LinearLayoutManager(getContext()));

        // Khởi tạo HikeAdapter với HikeDao
        adapter = new HikeAdapter(getContext(), null, HikeDatabase.getDatabase(getContext()).hikeDao(), false);
        recyclerView.setAdapter(adapter);

        // Load hikes and observe changes
        db.hikeDao().getAllHikeNames("%").observe(getViewLifecycleOwner(), hikes -> adapter.setHikes(hikes));


        loadHikes();

        Button deleteAllButton = view.findViewById(R.id.btnDeleteAll);
        deleteAllButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                deleteAllHikes();
            }
        });

        return view;
    }

    private void loadHikes() {
        // Quan sát LiveData từ HikeDao
        db.hikeDao().getAllHikeNames("%").observe(getViewLifecycleOwner(), new Observer<List<Hike>>() {
            @Override
            public void onChanged(List<Hike> hikes) {
                // Cập nhật dữ liệu vào adapter
                adapter.setHikes(hikes);
            }
        });
    }

    private void deleteAllHikes() {
        new Thread(() -> {
            db.hikeDao().deleteAll();
            getActivity().runOnUiThread(() -> {
                // Cập nhật giao diện người dùng sau khi xóa
                adapter.setHikes(new ArrayList<>());
            });
        }).start();
    }

}

