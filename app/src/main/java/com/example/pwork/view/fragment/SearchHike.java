package com.example.pwork.view.fragment;

import android.os.Bundle;
import android.text.Editable;
import android.text.TextWatcher;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.EditText;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
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

public class SearchHike extends Fragment {
    private RecyclerView recyclerView;
    private HikeAdapter adapter;
    private EditText searchEditText;
    private HikeDatabase db;
    private HikeDao hikeDao;

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        View view = inflater.inflate(R.layout.fragment_search_hike, container, false);
        searchEditText = view.findViewById(R.id.searchEditText);
        recyclerView = view.findViewById(R.id.resultRecyclerView);
        recyclerView.setLayoutManager(new LinearLayoutManager(getContext()));

        db = HikeDatabase.getDatabase(getContext());
        hikeDao = db.hikeDao();

        adapter = new HikeAdapter(getContext(), new ArrayList<>(), HikeDatabase.getDatabase(getContext()).hikeDao(), true);
        recyclerView.setAdapter(adapter);

        searchEditText.addTextChangedListener(new TextWatcher() {
            @Override
            public void beforeTextChanged(CharSequence s, int start, int count, int after) { }

            @Override
            public void onTextChanged(CharSequence s, int start, int before, int count) {
                performSearch(s.toString());
            }

            @Override
            public void afterTextChanged(Editable s) { }
        });

        return view;
    }

    private void loadHikes(String query) {
        String searchQuery = "%" + query + "%";
        db.hikeDao().getAllHikeNames(searchQuery).observe(getViewLifecycleOwner(), new Observer<List<Hike>>() {
            @Override
            public void onChanged(@Nullable final List<Hike> hikes) {
                adapter.setHikes(hikes); //cập nhật danh sách hikes trong adapter
            }
        });
    }

    private void performSearch(String searchQuery) {
        if (searchQuery.isEmpty()) {
            adapter.setHikes(new ArrayList<>()); //nếu chuỗi tìm kiếm trống, xóa kết quả hiện tại
        } else {
            final String finalSearchQuery = "%" + searchQuery + "%"; //thêm dấu % để tìm kiếm LIKE trong SQL
            new Thread(() -> {
                List<Hike> result = hikeDao.searchHikesByName(finalSearchQuery);
                getActivity().runOnUiThread(() -> {
                    adapter.setHikes(result); //cập nhật kết quả tìm kiếm vào adapter
                });
            }).start();
        }
    }
}
