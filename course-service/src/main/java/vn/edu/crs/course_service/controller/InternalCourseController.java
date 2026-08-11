package vn.edu.crs.course_service.controller;

import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PatchMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import vn.edu.crs.course_service.dto.CourseDTO;
import vn.edu.crs.course_service.service.CourseService;

@RestController
@RequestMapping("/internal/courses")
@RequiredArgsConstructor
public class InternalCourseController {

    private final CourseService courseService;

    @PatchMapping("/{id}/reserve-seat")
    public ResponseEntity<CourseDTO> reserveSeat(@PathVariable Long id) {
        return ResponseEntity.ok(courseService.reserveSeat(id));
    }

    @PatchMapping("/{id}/release-seat")
    public ResponseEntity<CourseDTO> releaseSeat(@PathVariable Long id) {
        return ResponseEntity.ok(courseService.releaseSeat(id));
    }
}
