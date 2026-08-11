package vn.edu.crs.registration_service.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import vn.edu.crs.registration_service.entity.Registration;

import java.util.List;

public interface RegistrationRepository extends JpaRepository<Registration, Long> {
    List<Registration> findByStudentId(Long studentId);
    boolean existsByStudentIdAndCourseIdAndTrangThai(Long studentId, Long courseId, String trangThai);
}
