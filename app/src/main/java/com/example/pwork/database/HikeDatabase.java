package com.example.pwork.database;

import android.content.Context;

import androidx.room.Database;
import androidx.room.Room;
import androidx.room.RoomDatabase;

import com.example.pwork.dao.HikeDao;
import com.example.pwork.model.Hike;

@Database(entities = {Hike.class}, version = 1, exportSchema = false)
public abstract class HikeDatabase extends RoomDatabase {

    public abstract HikeDao hikeDao();

    private static volatile HikeDatabase INSTANCE;

    public static HikeDatabase getDatabase(final Context context) {
        if (INSTANCE == null) {
            synchronized (HikeDatabase.class) {
                if (INSTANCE == null) {
                    INSTANCE = Room.databaseBuilder(context.getApplicationContext(),
                                    HikeDatabase.class, "hike_database")
                            .fallbackToDestructiveMigration()
                            .build();
                }
            }
        }
        return INSTANCE;
    }
}
