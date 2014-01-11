--
-- PostgreSQL database dump
--

-- Dumped from database version 9.2.5
-- Dumped by pg_dump version 9.3.1
-- Started on 2013-12-03 19:12:44 PST

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- TOC entry 184 (class 3079 OID 12595)
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;
CREATE EXTENSION pg_trgm;

--
-- TOC entry 2903 (class 0 OID 0)
-- Dependencies: 184
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- TOC entry 174 (class 1259 OID 16668)
-- Name: communities; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

DROP database if exists ethea;

CREATE DATABASE ethea
  WITH OWNER = postgres
       ENCODING = 'UTF8'
       TABLESPACE = pg_default
       LC_COLLATE = 'en_US.UTF-8'
       LC_CTYPE = 'en_US.UTF-8'
       CONNECTION LIMIT = -1       
       TEMPLATE template0;
\connect ethea
CREATE EXTENSION pg_trgm;

--
-- TOC entry 168 (class 1259 OID 17050)
-- Name: communities; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE communities (
    id uuid NOT NULL,
    name character varying(255),
    description character varying(2048),
    created timestamp without time zone,
    updated timestamp without time zone,
    image character varying(255)
);


ALTER TABLE public.communities OWNER TO postgres;

--
-- TOC entry 169 (class 1259 OID 17056)
-- Name: communities_itemtypes; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE communities_itemtypes (
    community_id uuid NOT NULL,
    itemtype_id uuid NOT NULL
);


ALTER TABLE public.communities_itemtypes OWNER TO postgres;

--
-- TOC entry 170 (class 1259 OID 17059)
-- Name: communities_profiles; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE communities_profiles (
    community_id uuid NOT NULL,
    profile_id uuid NOT NULL,
    flag character varying(255),    
    created timestamp without time zone,
    updated timestamp without time zone
);


ALTER TABLE public.communities_profiles OWNER TO postgres;

--
-- TOC entry 171 (class 1259 OID 17062)
-- Name: itemlists; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE itemlists (
    id uuid NOT NULL,
    name character varying(255),
    profile_id uuid,
    created timestamp without time zone,
    updated timestamp without time zone
);


ALTER TABLE public.itemlists OWNER TO postgres;

--
-- TOC entry 183 (class 1259 OID 17472)
-- Name: itemlists_items; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE itemlists_items (
    item_id uuid NOT NULL,
    itemlist_id uuid NOT NULL
);


ALTER TABLE public.itemlists_items OWNER TO postgres;

--
-- TOC entry 172 (class 1259 OID 17068)
-- Name: items; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE items (
    id uuid NOT NULL,
    name character varying(255),
    image character varying(255),
    itemtype_id uuid,
    description character varying(2048),
    flag character varying(255),
    created timestamp without time zone,
    updated timestamp without time zone
);


ALTER TABLE public.items OWNER TO postgres;

--
-- TOC entry 173 (class 1259 OID 17074)
-- Name: itemtype; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE itemtypes (
    id uuid NOT NULL,
    image character varying(255),
    name character varying(255),
    description character varying(2048),
    created timestamp without time zone,
    updated timestamp without time zone
);


ALTER TABLE public.itemtypes OWNER TO postgres;

--
-- TOC entry 174 (class 1259 OID 17080)
-- Name: messages; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE messages (
    id uuid NOT NULL,
    from_id uuid,
    to_id uuid,
    content character varying(1024),
    created timestamp without time zone,
    updated timestamp without time zone
);


ALTER TABLE public.messages OWNER TO postgres;

--
-- TOC entry 175 (class 1259 OID 17086)
-- Name: posts; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE posts (
    id uuid NOT NULL,
    title character varying(255),
    content character varying(2048),
    profile_id uuid,
    community_id uuid,
    likes integer,
    parent_id uuid,
    flag character varying(255),
    root_id uuid,
    deleted boolean DEFAULT FALSE,
    created timestamp without time zone,
    updated timestamp without time zone
);


ALTER TABLE public.posts OWNER TO postgres;

--
-- TOC entry 176 (class 1259 OID 17092)
-- Name: posts_items; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE posts_items (
    structure_id uuid NOT NULL,
    item_id uuid NOT NULL
);


ALTER TABLE public.posts_items OWNER TO postgres;

CREATE TABLE ethean_groups (
    ethean_id uuid NOT NULL,
    profile_id uuid,
    other_id uuid,
    group_name character varying(255) NOT NULL
);

ALTER TABLE public.ethean_groups OWNER TO postgres;

--
-- TOC entry 177 (class 1259 OID 17095)
-- Name: posts_tags; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE posts_tags (
    post_id uuid NOT NULL,
    tag_id uuid NOT NULL
);


ALTER TABLE public.posts_tags OWNER TO postgres;

--
-- TOC entry 178 (class 1259 OID 17098)
-- Name: profiles; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE profiles (
    id uuid NOT NULL,
    name character varying(255),
    ethean_id uuid,
    image character varying(255),
    description character varying(2048),
    created timestamp without time zone,
    updated timestamp without time zone
);


ALTER TABLE public.profiles OWNER TO postgres;

--
-- TOC entry 179 (class 1259 OID 17104)
-- Name: structures; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE structures (
    id uuid NOT NULL,
    content character varying(4048),
    post_id uuid,
    structure_type character varying(255),
    created timestamp without time zone,
    updated timestamp without time zone,
    insert_pos integer
);


ALTER TABLE public.structures OWNER TO postgres;

--
-- TOC entry 180 (class 1259 OID 17110)
-- Name: suggestion; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE suggestion (
    id uuid NOT NULL,
    title character varying(255),
    content character varying(1024),
    profile_id uuid,
    item_id uuid,
    created timestamp without time zone,
    updated timestamp without time zone
);


ALTER TABLE public.suggestion OWNER TO postgres;

--
-- TOC entry 181 (class 1259 OID 17116)
-- Name: tags; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE tags (
    id uuid NOT NULL,
    name character varying(255),
    created timestamp without time zone,
    updated timestamp without time zone
);


ALTER TABLE public.tags OWNER TO postgres;

--
-- TOC entry 182 (class 1259 OID 17119)
-- Name: etheans; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE etheans (
    name character varying(255),
    email character varying(255),
    id uuid NOT NULL,
    hashed_pwd character varying(512),
    access_token character varying(512),
    email_token character varying(512),
    flag character varying(255),
    created timestamp without time zone,
    updated timestamp without time zone,
    salt character varying(25),
    pwd_tk character varying(40)
);


ALTER TABLE public.etheans OWNER TO postgres;

--
-- TOC entry 2946 (class 0 OID 0)
-- Dependencies: 6
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;

