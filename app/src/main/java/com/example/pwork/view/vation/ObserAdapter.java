package com.example.pwork.view.vation;

import android.content.Context;
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
    @Override
    public int getItemCount() {
        return observations != null ? observations.size() : 0;
    }

    public static class ViewHolder extends RecyclerView.ViewHolder {
        TextView textViewObservation; // TextView for observation
        Button deleteItem; // Button for deleting the item

        public ViewHolder(View itemView) {
            super(itemView);
            textViewObservation = itemView.findViewById(R.id.textViewName);
            deleteItem = itemView.findViewById(R.id.deleteItem); // Add this line to find the delete button
        }
    }
}
