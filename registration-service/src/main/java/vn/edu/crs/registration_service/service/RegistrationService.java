package vn.edu.crs.registration_service.service;

import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import vn.edu.crs.registration_service.client.CourseClient;
import vn.edu.crs.registration_service.dto.RegistrationRequestDTO;
import vn.edu.crs.registration_service.entity.Registration;
import vn.edu.crs.registration_service.repository.RegistrationRepository;

import java.time.LocalDateTime;

@Service
@RequiredArgsConstructor
public class RegistrationService {

    private final RegistrationRepository registrationRepository;
    private final CourseClient courseClient;

    @Transactional
    public Registration register(RegistrationRequestDTO requestDTO) {
        if (registrationRepository.existsByStudentIdAndCourseIdAndTrangThai(
                requestDTO.getStudentId(), requestDTO.getCourseId(), "DA_DANG_KY")) {
            throw new IllegalStateException("Sinh vien da dang ky mon hoc nay");
        }

        // Call course-service to reserve seat
        courseClient.reserveSeat(requestDTO.getCourseId());

        Registration registration = new Registration();
        registration.setStudentId(requestDTO.getStudentId());
        registration.setCourseId(requestDTO.getCourseId());
        registration.setTrangThai("DA_DANG_KY");
        registration.setNgayDangKy(LocalDateTime.now());

        return registrationRepository.save(registration);
    }

    @Transactional
    public void cancel(Long registrationId) {
        Registration registration = registrationRepository.findById(registrationId)
                .orElseThrow(() -> new IllegalArgumentException("Khong tim thay ma dang ky"));

        if ("DA_HUY".equals(registration.getTrangThai())) {
            throw new IllegalStateException("Dang ky nay da bi huy tu truoc");
        }

        // Call course-service to release seat
        courseClient.releaseSeat(registration.getCourseId());

        registration.setTrangThai("DA_HUY");
        registrationRepository.save(registration);
    }
}
