package com.example.pwork.view;


import android.app.DatePickerDialog;
import android.os.Bundle;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.RadioButton;
import android.widget.RadioGroup;
import android.widget.Spinner;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.example.pwork.R;
import com.example.pwork.dao.HikeDao;
import com.example.pwork.database.HikeDatabase;
import com.example.pwork.model.Hike;

import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;
import java.util.Locale;

public class EditHike extends AppCompatActivity {
    private EditText hikeNameEditText, locationEditText, dateEditText, lengthEditText, descriptionEditText;
    private RadioGroup parkingRadioGroup;
    private Spinner difficultySpinner;
    private Button btnUpdate;
    private HikeDao hikeDao;
    private long hikeId;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_edit_hike);

        // Initialize views
        hikeNameEditText = findViewById(R.id.hikeNameEditText);
        locationEditText = findViewById(R.id.locationEditText);
        dateEditText = findViewById(R.id.dateEditText);
        lengthEditText = findViewById(R.id.lengthEditText);
        descriptionEditText = findViewById(R.id.descriptionEditText);
        parkingRadioGroup = findViewById(R.id.parkingRadioGroup);
        difficultySpinner = findViewById(R.id.difficultySpinner);
        btnUpdate = findViewById(R.id.btnUpdate);

        // Setup HikeDatabase and HikeDao
        HikeDatabase db = HikeDatabase.getDatabase(this);
        hikeDao = db.hikeDao();

        ArrayAdapter<CharSequence> adapter = ArrayAdapter.createFromResource(this,
                R.array.difficulty_levels, android.R.layout.simple_spinner_item);
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        difficultySpinner.setAdapter(adapter);

        dateEditText.setOnClickListener(v -> showDatePickerDialog());

        // Get hike ID from Intent
        hikeId = getIntent().getLongExtra("hike_id", -1);

        loadHikeData();

        btnUpdate.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                updateHike();
            }
        });
    }

    private void loadHikeData() {
        new Thread(() -> {
            Hike hike = hikeDao.getHikeById(hikeId);
            if (hike != null) {
                runOnUiThread(() -> {
                    hikeNameEditText.setText(hike.name);
                    locationEditText.setText(hike.location);
                    dateEditText.setText(hike.date);
                    lengthEditText.setText(String.valueOf(hike.length));
                    descriptionEditText.setText(hike.description);

                    // Set parking availability
                    RadioButton parkingAvailableButton = parkingRadioGroup.findViewById(
                            hike.parkingAvailable ? R.id.parkingAvailableRadioButton : R.id.parkingNotAvailableRadioButton);
                    if (parkingAvailableButton != null) {
                        parkingAvailableButton.setChecked(true);
                    }

                    // Set difficulty level
                    setSpinnerToValue(difficultySpinner, hike.difficulty);
                });
            }
        }).start();
    }

    private void updateHike() {
        new Thread(() -> {
            Hike hike = new Hike();
            hike.id = hikeId;
            hike.name = hikeNameEditText.getText().toString();
            hike.location = locationEditText.getText().toString();
            hike.date = dateEditText.getText().toString();
            hike.length = Integer.parseInt(lengthEditText.getText().toString());
            hike.description = descriptionEditText.getText().toString();

            // Update parking availability
            hike.parkingAvailable = parkingRadioGroup.getCheckedRadioButtonId() == R.id.parkingAvailableRadioButton;

            // Update difficulty level
            hike.difficulty = difficultySpinner.getSelectedItem().toString();

            hikeDao.updateHike(hike);

            runOnUiThread(() -> Toast.makeText(EditHike.this, "Hike updated", Toast.LENGTH_SHORT).show());
        }).start();
    }

    private void setSpinnerToValue(Spinner spinner, String value) {
        ArrayAdapter<CharSequence> adapter = (ArrayAdapter<CharSequence>) spinner.getAdapter();
        if (adapter != null) {
            for (int position = 0; position < adapter.getCount(); position++) {
                if (adapter.getItem(position).equals(value)) {
                    spinner.setSelection(position);
                    return;
                }
            }
        }
    }
    private void showDatePickerDialog() {
        final Calendar calendar = Calendar.getInstance();
        int year, month, day;

        // Kiểm tra xem EditText có chứa ngày hợp lệ không
        String currentText = dateEditText.getText().toString();
        if (!currentText.isEmpty()) {
            // Parse ngày từ EditText và sử dụng nó làm ngày mặc định trong DatePickerDialog
            SimpleDateFormat format = new SimpleDateFormat("yyyy-MM-dd", Locale.getDefault());
            try {
                Date date = format.parse(currentText);
                calendar.setTime(date);
            } catch (ParseException e) {
                e.printStackTrace();
            }
        }

        year = calendar.get(Calendar.YEAR);
        month = calendar.get(Calendar.MONTH);
        day = calendar.get(Calendar.DAY_OF_MONTH);

        DatePickerDialog datePickerDialog = new DatePickerDialog(this,
                (view, year1, monthOfYear, dayOfMonth) -> {
                    String selectedDate = String.format(Locale.getDefault(), "%d-%02d-%02d", year1, monthOfYear + 1, dayOfMonth);
                    dateEditText.setText(selectedDate);
                }, year, month, day);

        datePickerDialog.show();
    }
}


