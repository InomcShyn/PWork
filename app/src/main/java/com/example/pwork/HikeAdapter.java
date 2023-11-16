package com.example.pwork;

import android.content.Context;
import android.content.Intent;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.example.pwork.dao.HikeDao;
import com.example.pwork.model.Hike;
import com.example.pwork.view.editview.EditHike;
import com.example.pwork.view.fragment.AddHike;
import com.example.pwork.view.fragment.DetailsHike;
import com.example.pwork.view.vation.Observations;

import java.util.List;

public class HikeAdapter extends RecyclerView.Adapter<HikeAdapter.HikeViewHolder> {

    private List<Hike> hikes;
    private HikeDao hikeDao;
    private LayoutInflater mInflater;
    private boolean isSearch;

    public HikeAdapter(Context context, List<Hike> hikes, HikeDao hikeDao, boolean isSearch) {
        this.hikes = hikes;
        this.hikeDao = hikeDao;
        this.mInflater = LayoutInflater.from(context);
        this.isSearch = isSearch;
    }

    @Override
    public HikeViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View itemView = mInflater.inflate(isSearch ? R.layout.search_hike_item : R.layout.hike_list_item, parent, false);
        return new HikeViewHolder(itemView, this, isSearch);
    }

    @Override
    public void onBindViewHolder(@NonNull HikeViewHolder holder, int position) {
        Hike hike = hikes.get(position);
        if (isSearch) {
            // Chỉ hiển thị tên trong tìm kiếm
            holder.tvHikeName.setText(hike.name);
        } else {
            // Hiển thị tên và nút xóa trong danh sách chi tiết
            holder.textViewName.setText(hike.name);
            holder.textViewName.setOnClickListener(v -> {
                // Mở EditHike và truyền thông tin của chuyến đi (ID hoặc dữ liệu khác) để chỉnh sửa
                Intent intent = new Intent(v.getContext(), EditHike.class);
                intent.putExtra("HIKE_ID", hike.id);
                v.getContext().startActivity(intent);
            });
            holder.moreItem.setVisibility(View.VISIBLE);
            holder.moreItem.setOnClickListener(v -> {
                // Mở hoạt động mới để hiển thị quan sát (Observations)
                Intent intent = new Intent(v.getContext(), Observations.class);
                intent.putExtra("HIKE_ID", hike.id); // Truyền ID của chuyến đi để hiển thị các quan sát tương ứng
                v.getContext().startActivity(intent);
            });
            if (holder.deleteButton != null) {
                holder.deleteButton.setVisibility(View.VISIBLE);
            }
        }
    }

    @Override
    public int getItemCount() {
        return hikes != null ? hikes.size() : 0;
    }

    public void setHikes(List<Hike> hikes) {
        this.hikes = hikes;
        notifyDataSetChanged();
    }

    // Phương thức để xóa hike từ danh sách và cơ sở dữ liệu
    public void deleteHike(int position) {
        Hike hikeToDelete = hikes.get(position);

        // Xóa dữ liệu từ database trên luồng nền
        new Thread(new Runnable() {
            @Override
            public void run() {
                hikeDao.deleteHike(hikeToDelete);
            }
        }).start();

        // Cập nhật adapter
        hikes.remove(position);
        notifyItemRemoved(position);
    }

    public static class HikeViewHolder extends RecyclerView.ViewHolder {
        TextView textViewName, tvHikeName;
        Button deleteButton, moreItem;

        public HikeViewHolder(View itemView, HikeAdapter adapter, boolean isSearch) {
            super(itemView);
            textViewName = itemView.findViewById(R.id.textViewName);
            tvHikeName = itemView.findViewById(R.id.tvHikeName);
            moreItem = itemView.findViewById(R.id.moreItem);
            if (!isSearch) {
                deleteButton = itemView.findViewById(R.id.deleteItem);
                if (deleteButton != null) {
                    deleteButton.setOnClickListener(v -> {
                        int position = getAdapterPosition();
                        if (position != RecyclerView.NO_POSITION) {
                            adapter.deleteHike(position);
                        }
                    });
                }
            } else {
                deleteButton = null; // No delete button in search layout
            }
        }
    }
}
