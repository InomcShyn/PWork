package com.example.pwork.dao;

import androidx.lifecycle.LiveData;
import androidx.room.Dao;
import androidx.room.Delete;
import androidx.room.Insert;
import androidx.room.OnConflictStrategy;
import androidx.room.Query;
import androidx.room.Update;

import com.example.pwork.model.Hike;

import java.util.List;

@Dao
public interface HikeDao {
    @Insert(onConflict = OnConflictStrategy.IGNORE)
    long insertHike(Hike hike);

    @Delete
    void deleteHike(Hike hike);

    @Query("DELETE FROM hikes")
    void deleteAll();

    @Query("SELECT * FROM hikes WHERE id = :hikeId")
    Hike getHikeById(long hikeId);

    @Update
    void updateHike(Hike hike);
    @Query("SELECT * FROM hikes WHERE name LIKE :searchQuery")
    List<Hike> searchHikesByName(String searchQuery);

    @Query("SELECT * FROM hikes WHERE name LIKE '%' || :name || '%'")
    LiveData<List<Hike>> getAllHikeNames(String name);
}

