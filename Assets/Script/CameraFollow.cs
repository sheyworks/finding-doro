using UnityEngine;
using UnityEngine.InputSystem;

public class CameraFollow : MonoBehaviour
{
    [SerializeField] private Transform target;
    [SerializeField] private float distance = 5f;
    [SerializeField] private float focusHeight = 1.1f;
    [SerializeField] private float mouseSensitivity = 0.12f;
    [SerializeField] private float minPitch = -10f;
    [SerializeField] private float maxPitch = 65f;

    private float yaw;
    private float pitch = 15f;

    private void Start()
    {
        FindTarget();
        if (target != null) yaw = target.eulerAngles.y;
        LockCursor();
    }

    private void LateUpdate()
    {
        FindTarget();
        if (target == null) return;

        Mouse mouse = Mouse.current;
        if (mouse != null && Cursor.lockState == CursorLockMode.Locked)
        {
            Vector2 mouseDelta = mouse.delta.ReadValue();
            yaw += mouseDelta.x * mouseSensitivity;
            pitch = Mathf.Clamp(pitch - mouseDelta.y * mouseSensitivity, minPitch, maxPitch);
        }

        Quaternion orbitRotation = Quaternion.Euler(pitch, yaw, 0f);
        Vector3 focusPoint = target.position + Vector3.up * focusHeight;
        transform.position = focusPoint + orbitRotation * new Vector3(0f, 0f, -distance);
        transform.rotation = orbitRotation;

        if (Keyboard.current != null && Keyboard.current.escapeKey.wasPressedThisFrame)
        {
            Cursor.lockState = CursorLockMode.None;
            Cursor.visible = true;
        }
        else if (mouse != null && mouse.leftButton.wasPressedThisFrame && Cursor.lockState != CursorLockMode.Locked)
        {
            LockCursor();
        }
    }

    private void FindTarget()
    {
        if (target != null) return;

        PlayerMovement player = FindFirstObjectByType<PlayerMovement>();
        if (player != null)
        {
            target = player.transform;
            yaw = target.eulerAngles.y;
        }
    }

    private static void LockCursor()
    {
        Cursor.lockState = CursorLockMode.Locked;
        Cursor.visible = false;
    }

    private void OnDisable()
    {
        Cursor.lockState = CursorLockMode.None;
        Cursor.visible = true;
    }
}
