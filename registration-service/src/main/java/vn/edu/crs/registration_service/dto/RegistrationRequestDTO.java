package vn.edu.crs.registration_service.dto;

import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class RegistrationRequestDTO {
    @NotNull(message = "Ma sinh vien khong duoc de trong")
    private Long studentId;

    @NotNull(message = "Ma mon hoc khong duoc de trong")
    private Long courseId;
}
