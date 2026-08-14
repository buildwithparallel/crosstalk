import Utils from "./Utils";

/**
 * Reticulum AutoInterface defaults. Empty optional fields in Crosstalk mean
 * these values, so two "blank" LAN interfaces share one UDP mesh.
 */
export const AUTO_INTERFACE_DEFAULT_GROUP_ID = "reticulum";
export const AUTO_INTERFACE_DEFAULT_DISCOVERY_PORT = 29716;
export const AUTO_INTERFACE_DEFAULT_DATA_PORT = 42671;

function firstPresent(value) {
    if(value === undefined || value === null){
        return "";
    }
    return String(value).trim();
}

function portOrDefault(value, fallback) {
    const parsed = Number(value);
    if(Number.isFinite(parsed) && parsed > 0){
        return parsed;
    }
    return fallback;
}

class AutoInterfaceUtils {

    /**
     * Group, discovery port, and data port that identify one AutoInterface mesh.
     * Unset fields resolve to Reticulum's defaults.
     */
    static meshIdentity(iface) {
        const groupId = firstPresent(iface?.group_id).toLowerCase() || AUTO_INTERFACE_DEFAULT_GROUP_ID;
        const discoveryPort = portOrDefault(iface?.discovery_port, AUTO_INTERFACE_DEFAULT_DISCOVERY_PORT);
        const dataPort = portOrDefault(iface?.data_port, AUTO_INTERFACE_DEFAULT_DATA_PORT);
        return `${groupId}|${discoveryPort}|${dataPort}`;
    }

    static withNames(interfaces) {
        return Object.entries(interfaces ?? {}).map(([name, iface]) => ({
            ...iface,
            _name: name,
        }));
    }

    static enabledAutoInterfaces(interfaces, excludeName = null) {
        return this.withNames(interfaces).filter((iface) => {
            if(iface.type !== "AutoInterface"){
                return false;
            }
            if(excludeName && iface._name === excludeName){
                return false;
            }
            return Utils.isInterfaceEnabled(iface);
        });
    }

    /**
     * First enabled AutoInterface that shares this form's mesh identity.
     */
    static conflictingEnabledAutoInterface(interfaces, candidate, excludeName = null) {
        const candidateIdentity = this.meshIdentity(candidate);
        return this.enabledAutoInterfaces(interfaces, excludeName).find((iface) => {
            return this.meshIdentity(iface) === candidateIdentity;
        }) ?? null;
    }

}

export default AutoInterfaceUtils;
