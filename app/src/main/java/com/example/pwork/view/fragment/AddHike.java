package com.example.pwork.view.fragment;

import android.app.AlertDialog;
import android.app.DatePickerDialog;
import android.content.DialogInterface;
import android.os.AsyncTask;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.DatePicker;
import android.widget.EditText;
import android.widget.RadioButton;
import android.widget.RadioGroup;
import android.widget.Spinner;
import android.widget.Toast;
import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;
import androidx.room.Room;

import com.example.pwork.database.HikeDatabase;
import com.example.pwork.R;
import com.example.pwork.model.Hike;

import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Locale;

public class AddHike extends Fragment {

    private EditText hikeNameEditText, locationEditText, dateEditText, lengthEditText, descriptionEditText;
    private RadioGroup parkingRadioGroup;
    private Spinner difficultySpinner;
    private Button addButton;

    private HikeDatabase hikeDatabase;

    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container,
                             @Nullable Bundle savedInstanceState) {
        View root = inflater.inflate(R.layout.fragment_add_hike, container, false);

        hikeNameEditText = root.findViewById(R.id.hikeNameEditText);
        locationEditText = root.findViewById(R.id.locationEditText);
        dateEditText = root.findViewById(R.id.dateEditText);
        lengthEditText = root.findViewById(R.id.lengthEditText);
        descriptionEditText = root.findViewById(R.id.descriptionEditText);
        parkingRadioGroup = root.findViewById(R.id.parkingRadioGroup);
        difficultySpinner = root.findViewById(R.id.difficultySpinner);
        addButton = root.findViewById(R.id.addButton);

        hikeDatabase = Room.databaseBuilder(requireContext(), HikeDatabase.class, "hike_database")
                .build();

        ArrayAdapter<CharSequence> spinnerAdapter = ArrayAdapter.createFromResource(requireContext(),
                R.array.difficulty_levels, android.R.layout.simple_spinner_item);
        spinnerAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        difficultySpinner.setAdapter(spinnerAdapter);

        RadioButton yesRadioButton = root.findViewById(R.id.parkingAvailableRadioButton);
        yesRadioButton.setChecked(true);

        addButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                addHikeToDatabase();
            }
        });

        dateEditText.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                showDatePickerDialog();
            }
        });

        return root;
    }

    private void addHikeToDatabase() {
        String name = hikeNameEditText.getText().toString();
        String location = locationEditText.getText().toString();
        String date = dateEditText.getText().toString();
        String lengthText = lengthEditText.getText().toString();
        String description = descriptionEditText.getText().toString();

        int selectedParkingId = parkingRadioGroup.getCheckedRadioButtonId();
        RadioButton selectedParking = getView().findViewById(selectedParkingId);
        boolean parkingAvailable = selectedParking.getText().toString().equals("Yes");

        String difficulty = difficultySpinner.getSelectedItem().toString();

        if (name.isEmpty() || location.isEmpty() || date.isEmpty() ||
                lengthText.isEmpty() || description.isEmpty()) {
            Toast.makeText(requireContext(), "Please fill in all required fields", Toast.LENGTH_SHORT).show();
        } else {
            int length = Integer.parseInt(lengthText);

            Hike hike = new Hike();
            hike.name = name;
            hike.location = location;
            hike.date = date;
            hike.parkingAvailable = parkingAvailable;
            hike.length = length;
            hike.difficulty = difficulty;
            hike.description = description;

            //hiển thị AlertDialog để xác nhận thông tin trước khi thêm vào cơ sở dữ liệu
            showConfirmationDialog(hike);
        }
    }

    private void showDatePickerDialog() {
        int year = Calendar.getInstance().get(Calendar.YEAR);
        int month = Calendar.getInstance().get(Calendar.MONTH);
        int day = Calendar.getInstance().get(Calendar.DAY_OF_MONTH);

        DatePickerDialog datePickerDialog = new DatePickerDialog(requireContext(),
                new DatePickerDialog.OnDateSetListener() {
                    @Override
                    public void onDateSet(DatePicker view, int year, int monthOfYear, int dayOfMonth) {
                        Calendar selectedDate = Calendar.getInstance();
                        selectedDate.set(year, monthOfYear, dayOfMonth);
                        SimpleDateFormat dateFormat = new SimpleDateFormat("dd/MM/yyyy", Locale.getDefault());
                        dateEditText.setText(dateFormat.format(selectedDate.getTime()));
                    }
                }, year, month, day);

        datePickerDialog.show();
    }

    private void showConfirmationDialog(final Hike hike) {
        AlertDialog.Builder builder = new AlertDialog.Builder(requireContext());
        builder.setTitle("Confirm Hike Details");
        builder.setMessage("Name: " + hike.name + "\nLocation: " + hike.location + "\nDate: " + hike.date +
                "\nParking Available: " + (hike.parkingAvailable ? "Yes" : "No") + "\nLength: " + hike.length +
                "\nDifficulty: " + hike.difficulty + "\nDescription: " + hike.description);

        builder.setPositiveButton("Confirm", new DialogInterface.OnClickListener() {
            @Override
            public void onClick(DialogInterface dialog, int which) {
                // Thêm hike vào cơ sở dữ liệu
                new InsertHikeTask().execute(hike);
            }
        });

        builder.setNegativeButton("Cancel", new DialogInterface.OnClickListener() {
            @Override
            public void onClick(DialogInterface dialog, int which) {
                dialog.dismiss();
            }
        });

        AlertDialog alertDialog = builder.create();
        alertDialog.show();
    }

    private class InsertHikeTask extends AsyncTask<Hike, Void, Long> {
        @Override
        protected Long doInBackground(Hike... hikes) {
            // Thêm hike vào cơ sở dữ liệu
            return hikeDatabase.hikeDao().insertHike(hikes[0]);
        }

        @Override
        protected void onPostExecute(Long result) {
            super.onPostExecute(result);
            if (result != -1) {
                Toast.makeText(requireContext(), "Hike added successfully", Toast.LENGTH_SHORT).show();
                clearInputFields();
            } else {
                Toast.makeText(requireContext(), "Error adding hike", Toast.LENGTH_SHORT).show();
            }
        }
    }

    private void clearInputFields() {
        hikeNameEditText.getText().clear();
        locationEditText.getText().clear();
        dateEditText.getText().clear();
        lengthEditText.getText().clear();
        descriptionEditText.getText().clear();
    }
}
