package vn.edu.crs.registration_service.client;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Component;
import org.springframework.web.client.HttpClientErrorException;
import org.springframework.web.client.RestTemplate;

@Component
public class CourseClient {

    private final RestTemplate restTemplate;
    private final String courseServiceBaseUrl;

    public CourseClient(RestTemplate restTemplate, @Value("${course-service.base-url}") String courseServiceBaseUrl) {
        this.restTemplate = restTemplate;
        this.courseServiceBaseUrl = courseServiceBaseUrl;
    }

    public void reserveSeat(Long courseId) {
        try {
            String url = courseServiceBaseUrl + "/internal/courses/" + courseId + "/reserve-seat";
            // The API expects a PATCH request
            restTemplate.patchForObject(url, null, Object.class);
        } catch (HttpClientErrorException.Conflict e) {
            throw new IllegalStateException("Mon hoc da het cho, khong the dang ky");
        } catch (HttpClientErrorException.NotFound e) {
            throw new IllegalArgumentException("Mon hoc khong ton tai");
        } catch (Exception e) {
            throw new RuntimeException("Khong the ket noi den course-service", e);
        }
    }

    public void releaseSeat(Long courseId) {
        try {
            String url = courseServiceBaseUrl + "/internal/courses/" + courseId + "/release-seat";
            // The API expects a PATCH request
            restTemplate.patchForObject(url, null, Object.class);
        } catch (HttpClientErrorException.NotFound e) {
            throw new IllegalArgumentException("Mon hoc khong ton tai");
        } catch (Exception e) {
            throw new RuntimeException("Khong the ket noi den course-service", e);
        }
    }
}
