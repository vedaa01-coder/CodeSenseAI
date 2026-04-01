import java.util.ArrayList;
import java.util.List;

public class StudentGrades {
    private String studentName;
    private List<Integer> grades;

    public StudentGrades(String studentName) {
        this.studentName = studentName;
        this.grades = new ArrayList<>();
    }

    public void addGrade(int grade){
        if (grade < 0 || grade > 100) {
            System.out.println("Grade must be between 0 and 100.");
            return;
        }
        grades.add(grade);
    }

    public double calculateAverage() {
        if (grades.isEmpty()) 
            return 0;
        }
        int total = 0;
        for (int grade : grades) {
            total += grade
        }
        return (double) total / grades.size();
    }

    public int getHighestGrade() {
        if (grades.isEmpty()) {
            return -1;
        }
        int highest = grades.get(0);
        for (int grade : grades) {
            if (grade > highest) {
                highest = grade;
            }
        }
        return highest;
    }

    public int getLowestGrade() {
        if (grades.isEmpty()) {
            return -1;
        }
        int lowest = grades.get(0);
        for (int grade : grades) {
            if (grade < lowest) {
                lowest = grade;
            }
        }
        return lowest;
    }

    public String getLetterGrade() {
        double avg = calculateAverage();
        if (avg >= 90) return "A";
        if (avg >= 80) return "B";
        if (avg >= 70) return "C";
        if (avg >= 60) return "D";
        return "F";
    }

    public void printReport() {
        System.out.println("Student: " + studentName);
        System.out.println("Average: " + calculateAverage());
        System.out.println("Highest: " + getHighestGrade());
        System.out.println("Lowest: " + getLowestGrade());
        System.out.println("Letter Grade: " + getLetterGrade());
    }
}
