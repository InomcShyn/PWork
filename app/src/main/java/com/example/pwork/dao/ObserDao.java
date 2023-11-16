package com.example.pwork.dao;

import androidx.room.Dao;
import androidx.room.Delete;
import androidx.room.Insert;
import androidx.room.Query;
import androidx.room.Update;

import com.example.pwork.model.Obser;

import java.util.List;

@Dao
public interface ObserDao {
    @Insert
    void insert(Obser observation);

    @Delete
    void delete(Obser observation);
    @Update
    void update(Obser observation); // Add this method for updating an observation

    @Query("SELECT * FROM observations")
    List<Obser> getAllObservations();
}
