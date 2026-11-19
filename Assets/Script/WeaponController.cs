using UnityEngine;

public class WeaponController : MonoBehaviour
{
    public Transform firePoint;
    public GameObject bulletPrefab;
    public float bulletForce = 20f;

    [SerializeField] private Camera aimCamera;
    [SerializeField] private RectTransform crosshair;
    [SerializeField] private float maxAimDistance = 500f;
    [SerializeField] private LayerMask aimLayers = Physics.DefaultRaycastLayers;
    [SerializeField] private float bulletLifetime = 2f;

    private void Awake()
    {
        ResolveAimReferences();
    }

    private void Update()
    {
        DrawAimDebug();

        if (Input.GetKeyDown(KeyCode.LeftControl))
        {
            Shoot();
        }
    }

    private void DrawAimDebug()
    {
        if (firePoint == null) return;

        ResolveAimReferences();
        if (aimCamera == null) return;

        Ray aimRay = aimCamera.ScreenPointToRay(GetCrosshairScreenPoint());
        Debug.DrawRay(aimRay.origin, aimRay.direction * maxAimDistance, Color.yellow);

        Vector3 direction = GetAimPoint(aimRay) - firePoint.position;
        if (direction.sqrMagnitude < 0.0001f) direction = aimRay.direction;
        direction.Normalize();
        Debug.DrawRay(firePoint.position, direction * maxAimDistance, Color.red);
    }

    private void Shoot()
    {
        if (firePoint == null || bulletPrefab == null) return;

        ResolveAimReferences();
        if (aimCamera == null) return;

        Vector2 screenPoint = GetCrosshairScreenPoint();
        Ray aimRay = aimCamera.ScreenPointToRay(screenPoint);
        Debug.DrawRay(aimRay.origin, aimRay.direction * maxAimDistance, Color.yellow);
        Vector3 aimPoint = GetAimPoint(aimRay);
        Vector3 direction = aimPoint - firePoint.position;
        if (direction.sqrMagnitude < 0.0001f)
        {
            direction = aimRay.direction;
        }
        direction.Normalize();
        Debug.DrawRay(firePoint.position, direction * maxAimDistance, Color.red);

        Quaternion bulletRotation = Quaternion.FromToRotation(firePoint.up, direction) * firePoint.rotation;
        GameObject bullet = Instantiate(bulletPrefab, firePoint.position, bulletRotation);
        IgnoreShooterCollisions(bullet);

        Rigidbody rb = bullet.GetComponent<Rigidbody>();
        if (rb != null)
        {
            rb.AddForce(direction * bulletForce, ForceMode.Impulse);
        }

        Destroy(bullet, bulletLifetime);
    }

    private Vector3 GetAimPoint(Ray aimRay)
    {
        Vector3 aimPoint = aimRay.GetPoint(maxAimDistance);
        float closestDistance = maxAimDistance;
        Transform shooterRoot = transform.root;

        RaycastHit[] hits = Physics.RaycastAll(
            aimRay,
            maxAimDistance,
            aimLayers,
            QueryTriggerInteraction.Ignore);

        foreach (RaycastHit hit in hits)
        {
            if (hit.collider == null || hit.transform == shooterRoot || hit.transform.IsChildOf(shooterRoot))
            {
                continue;
            }

            if (hit.distance < closestDistance)
            {
                closestDistance = hit.distance;
                aimPoint = hit.point;
            }
        }

        return aimPoint;
    }

    private Vector2 GetCrosshairScreenPoint()
    {
        if (crosshair == null)
        {
            return new Vector2(Screen.width * 0.5f, Screen.height * 0.5f);
        }

        Canvas canvas = crosshair.GetComponentInParent<Canvas>();
        Camera canvasCamera = canvas != null && canvas.renderMode != RenderMode.ScreenSpaceOverlay
            ? canvas.worldCamera
            : null;

        return RectTransformUtility.WorldToScreenPoint(canvasCamera, crosshair.position);
    }

    private void ResolveAimReferences()
    {
        if (aimCamera == null) aimCamera = Camera.main;

        if (crosshair == null)
        {
            GameObject crosshairObject = GameObject.Find("Crosshair");
            if (crosshairObject != null) crosshair = crosshairObject.GetComponent<RectTransform>();
        }
    }

    private void IgnoreShooterCollisions(GameObject bullet)
    {
        Collider[] bulletColliders = bullet.GetComponentsInChildren<Collider>();
        Collider[] shooterColliders = transform.root.GetComponentsInChildren<Collider>();

        foreach (Collider bulletCollider in bulletColliders)
        {
            foreach (Collider shooterCollider in shooterColliders)
            {
                if (bulletCollider != null && shooterCollider != null)
                {
                    Physics.IgnoreCollision(bulletCollider, shooterCollider);
                }
            }
        }
    }
}
