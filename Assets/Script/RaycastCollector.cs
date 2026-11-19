using UnityEngine;

public class RaycastCollector : MonoBehaviour
{
    public Camera mainCamera;
    public float raycastDistance = 4.0f;
    public bool showDebugRay = true;
    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        if (mainCamera == null)
        {
            mainCamera = Camera.main;
        }
    }

    // Update is called once per frame
    void Update()
    {
        if(showDebugRay && mainCamera != null)
        {
            Ray rayDebug = new Ray(mainCamera.transform.position, mainCamera.transform.forward);
            Debug.DrawRay(rayDebug.origin, rayDebug.direction * raycastDistance, Color.green);
        }

        if(Input.GetKeyDown(KeyCode.C) && mainCamera != null)
        {
            Ray ray = new Ray(mainCamera.transform.position, mainCamera.transform.forward);
            if(Physics.Raycast(ray, out RaycastHit hitInfo, raycastDistance))
            {
                Collectible collectible = hitInfo.collider.GetComponent<Collectible>();
                if(collectible != null)
                {
                    collectible.Collect();
                }
            }
        }
    }

    void tryCollect()
    {
        if (mainCamera == null) return;
        
        Vector3 centerScreenPoint = new Vector3(Screen.width / 2f, Screen.height / 2f, 0f);
        Ray ray = mainCamera.ScreenPointToRay(centerScreenPoint);

        RaycastHit hitInfo;

        if (Physics.Raycast(ray, out hitInfo, raycastDistance))
        {
            Collectible collectible = hitInfo.collider.GetComponent<Collectible>();
            if(hitInfo.collider.CompareTag("Collectible"))
            {
                Debug.Log($"Hit Collectible: {hitInfo.collider.name}");
                Collectible collectibleComponent = hitInfo.collider.GetComponent<Collectible>();
            }
            
        }
    }
}
