package com.example.pwork.view.vation;

import android.content.Context;
import android.content.Intent;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.example.pwork.R;
import com.example.pwork.database.HikeDatabase;
import com.example.pwork.model.Obser;
import com.example.pwork.view.editview.EditOb;

import java.util.List;

public class ObserAdapter extends RecyclerView.Adapter<ObserAdapter.ViewHolder> {
    private List<Obser> observations;
    private Context context;
    private HikeDatabase db;

    public ObserAdapter(Context context, List<Obser> observations, HikeDatabase database) {
        this.context = context;
        this.observations = observations;
        this.db = database;
    }

    @NonNull
    @Override
    public ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext()).inflate(R.layout.ob_list_item, parent, false);
        return new ViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull ViewHolder holder, int position) {
        Obser observation = observations.get(position);
        // Thiết lập các view trong holder, ví dụ: hiển thị thông tin quan sát
        holder.textViewObservation.setText(observation.observation);

        // Xử lý sự kiện khi nút "Delete" được nhấn
        holder.deleteItem.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                // Lấy vị trí của item trong danh sách
                int adapterPosition = holder.getAdapterPosition();
                if (adapterPosition != RecyclerView.NO_POSITION) {
                    // Xử lý xóa quan sát ở vị trí này
                    removeObservation(adapterPosition);
                }
            }
        });

        // Xử lý sự kiện khi nút "Edit" được nhấn
        holder.editItem.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                // Lấy vị trí của item trong danh sách
                int adapterPosition = holder.getAdapterPosition();
                if (adapterPosition != RecyclerView.NO_POSITION) {
                    // Xử lý chỉnh sửa quan sát ở vị trí này và chuyển sang màn hình EditOb
                    editObservation(adapterPosition);
                }
            }
        });
    }

    public void removeObservation(int position) {
        Obser observation = observations.get(position);

        // Xóa quan sát khỏi cơ sở dữ liệu
        new Thread(new Runnable() {
            @Override
            public void run() {
                db.observationDao().delete(observation);
            }
        }).start();

        // Sau khi xóa thành công từ cơ sở dữ liệu, tiến hành xóa khỏi danh sách và cập nhật giao diện
        observations.remove(position);
        notifyItemRemoved(position);
    }

    // Phương thức để chỉnh sửa quan sát tại vị trí cụ thể
    public void editObservation(int position) {
        Obser observation = observations.get(position);

        // Tạo một Intent để chuyển sang màn hình EditOb
        Intent intent = new Intent(context, EditOb.class);

        // Truyền dữ liệu của quan sát cần chỉnh sửa vào Intent
        intent.putExtra("observation_id", observation.id); // Truyền ID của quan sát
        intent.putExtra("observation_observation", observation.observation); // Truyền thông tin quan sát
        intent.putExtra("observation_time", observation.timeOfObservation); // Truyền thời gian quan sát
        intent.putExtra("observation_comments", observation.comments); // Truyền bình luận

        // Bắt đầu màn hình EditOb bằng Intent
        context.startActivity(intent);
    }

    @Override
    public int getItemCount() {
        return observations != null ? observations.size() : 0;
    }

    public static class ViewHolder extends RecyclerView.ViewHolder {
        TextView textViewObservation; // TextView for observation
        Button deleteItem; // Button for deleting the item
        Button editItem; // Button for editing the item

        public ViewHolder(View itemView) {
            super(itemView);
            textViewObservation = itemView.findViewById(R.id.textViewName);
            deleteItem = itemView.findViewById(R.id.deleteItem);
            editItem = itemView.findViewById(R.id.editItem); // Add this line to find the edit button
        }
    }
}
