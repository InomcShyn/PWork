package com.example.pwork.model;

import androidx.room.Entity;
import androidx.room.PrimaryKey;

@Entity(tableName = "hikes")
public class Hike {
    @PrimaryKey(autoGenerate = true)
    public long id;
    public String name;
    public String location;
    public String date;
    public boolean parkingAvailable;
    public int length;
    public String difficulty;
    public String description;
}

