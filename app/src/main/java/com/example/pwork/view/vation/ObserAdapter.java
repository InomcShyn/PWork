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
        //Thiết lập các view trong holder
        holder.textViewObservation.setText(observation.observation);

        //Xử lý sự kiện khi nút "Delete" được nhấn
        holder.deleteItem.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                //Lấy vị trí của item trong danh sách
                int adapterPosition = holder.getAdapterPosition();
                if (adapterPosition != RecyclerView.NO_POSITION) {
                    // Xử lý xóa quan sát ở vị trí này
                    removeObservation(adapterPosition);
                }
            }
        });

        holder.editItem.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                //Lấy vị trí của item trong danh sách
                int adapterPosition = holder.getAdapterPosition();
                if (adapterPosition != RecyclerView.NO_POSITION) {
                    editObservation(adapterPosition);
                }
            }
        });
    }

    public void removeObservation(int position) {
        Obser observation = observations.get(position);

        //Xóa quan sát khỏi cơ sở dữ liệu
        new Thread(new Runnable() {
            @Override
            public void run() {
                db.observationDao().delete(observation);
            }
        }).start();

        observations.remove(position);
        notifyItemRemoved(position);
    }

    public void editObservation(int position) {
        Obser observation = observations.get(position);

        //Tạo một Intent để chuyển sang màn hình EditOb
        Intent intent = new Intent(context, EditOb.class);

        //Truyền dữ liệu của quan sát cần chỉnh sửa vào Intent
        intent.putExtra("observation_id", observation.id);
        intent.putExtra("observation_observation", observation.observation);
        intent.putExtra("observation_time", observation.timeOfObservation);
        intent.putExtra("observation_comments", observation.comments);

        //Bắt đầu màn hình EditOb bằng Intent
        context.startActivity(intent);
    }

    @Override
    public int getItemCount() {
        return observations != null ? observations.size() : 0;
    }

    public static class ViewHolder extends RecyclerView.ViewHolder {
        TextView textViewObservation;
        Button deleteItem;
        Button editItem;

        public ViewHolder(View itemView) {
            super(itemView);
            textViewObservation = itemView.findViewById(R.id.textViewName);
            deleteItem = itemView.findViewById(R.id.deleteItem);
            editItem = itemView.findViewById(R.id.editItem);
        }
    }
}
